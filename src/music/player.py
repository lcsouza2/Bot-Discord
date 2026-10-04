"""Gerenciador de fila e reprodução por servidor (GuildMusicPlayer)."""

from __future__ import annotations

import asyncio
from typing import Optional, List
import logging
import discord

from src.music.models import LoopMode, Track
from src.music.ytdl import YTDLSource

logger = logging.getLogger(__name__)


class GuildMusicPlayer:
    """Gerencia a fila e reprodução contínua para um servidor do Discord."""

    def __init__(self, bot: discord.Client, guild: discord.Guild) -> None:
        self.bot = bot
        self.guild = guild
        self.queue: List[Track] = []
        self.current: Optional[Track] = None
        self.loop_mode: LoopMode = LoopMode.OFF
        self.volume: float = 0.5
        self.text_channel: Optional[discord.abc.Messageable] = None

        self._next_song_event = asyncio.Event()
        self._player_task: Optional[asyncio.Task[None]] = None
        self._source: Optional[discord.PCMVolumeTransformer] = None
        self._is_stopped = False

    @property
    def voice_client(self) -> Optional[discord.VoiceClient]:
        """Obtém o VoiceClient ativo no servidor."""
        return self.guild.voice_client  # type: ignore[return-value]

    @property
    def is_playing(self) -> bool:
        """Verifica se há áudio sendo reproduzido no momento."""
        vc = self.voice_client
        return vc is not None and vc.is_playing()

    @property
    def is_paused(self) -> bool:
        """Verifica se a reprodução atual está pausada."""
        vc = self.voice_client
        return vc is not None and vc.is_paused()

    def start_if_needed(self) -> None:
        """Inicia a task do loop de reprodução se não estiver ativa."""
        if self._player_task is None or self._player_task.done():
            self._is_stopped = False
            self._player_task = asyncio.create_task(self._player_loop())

    def enqueue(self, tracks: List[Track]) -> int:
        """Adiciona faixas à fila e inicia o player se necessário."""
        self.queue.extend(tracks)
        self.start_if_needed()
        return len(tracks)

    def skip(self) -> bool:
        """Avança para a próxima faixa da fila."""
        vc = self.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            # Se estiver em loop de track único, skip manual força ir para a próxima
            if self.loop_mode == LoopMode.TRACK:
                self.loop_mode = LoopMode.OFF
            vc.stop()
            return True
        return False

    def pause(self) -> bool:
        """Pausa a reprodução atual."""
        vc = self.voice_client
        if vc and vc.is_playing():
            vc.pause()
            return True
        return False

    def resume(self) -> bool:
        """Retoma a reprodução pausada."""
        vc = self.voice_client
        if vc and vc.is_paused():
            vc.resume()
            return True
        return False

    def stop(self) -> None:
        """Para a reprodução e limpa a fila."""
        self._is_stopped = True
        self.queue.clear()
        self.current = None
        vc = self.voice_client
        if vc:
            vc.stop()
        self._next_song_event.set()

    def clear(self) -> int:
        """Limpa as faixas pendentes da fila sem parar a música atual."""
        count = len(self.queue)
        self.queue.clear()
        return count

    def set_volume(self, volume: float) -> float:
        """Define o volume entre 0.0 e 2.0 (0% a 200%)."""
        clamped = max(0.0, min(volume, 2.0))
        self.volume = clamped
        if self._source:
            self._source.volume = clamped
        return clamped

    def set_loop_mode(self, mode: LoopMode) -> LoopMode:
        """Altera o modo de repetição."""
        self.loop_mode = mode
        return self.loop_mode

    def _play_next_callback(self, error: Optional[Exception] = None) -> None:
        """Callback executado pelo discord.py quando uma faixa conclui o streaming."""
        if error:
            logger.error("Erro na reprodução de áudio: %s", error)

        # Notifica o loop para processar a próxima música
        self.bot.loop.call_soon_threadsafe(self._next_song_event.set)

    async def _player_loop(self) -> None:
        """Loop contínuo que processa a fila de músicas."""
        await self.bot.wait_until_ready()

        while not self._is_stopped:
            self._next_song_event.clear()

            # Trata repetições antes de desenfileirar
            if self.current is not None:
                if self.loop_mode == LoopMode.TRACK:
                    # Repete a mesma faixa: mantém self.current
                    pass
                elif self.loop_mode == LoopMode.QUEUE:
                    # Adiciona a faixa recém-tocada de volta ao final da fila
                    self.queue.append(self.current)
                    self.current = None
                else:
                    self.current = None

            # Se não estiver repetindo a faixa atual, pega a próxima da fila
            if self.current is None:
                if not self.queue:
                    # Fila vazia: aguarda até 300 segundos por novas músicas
                    try:
                        await asyncio.wait_for(self._wait_for_queue_or_stop(), timeout=300.0)
                    except asyncio.TimeoutError:
                        # Timeout por inatividade: desconecta do canal de voz
                        await self._handle_inactivity_disconnect()
                        break

                    if self._is_stopped or not self.queue:
                        continue

                self.current = self.queue.pop(0)

            vc = self.voice_client
            if not vc or not vc.is_connected():
                # Sem conexão de voz, aguarda nova conexão
                await asyncio.sleep(1)
                continue

            try:
                source = YTDLSource.create_audio_source(self.current, volume=self.volume)
                self._source = source
                vc.play(source, after=self._play_next_callback)

                # Anuncia a música no canal de texto se disponível
                if self.text_channel:
                    await self._announce_now_playing(self.current)

            except Exception as exc:
                logger.error("Falha ao iniciar reprodução da faixa '%s': %s", self.current.title, exc)
                if self.text_channel:
                    try:
                        await self.text_channel.send(
                            f"⚠️ Não foi possível reproduzir **{self.current.title}**: `{exc}`"
                        )
                    except Exception:
                        pass
                self.current = None
                continue

            # Aguarda a conclusão da música atual
            await self._next_song_event.wait()

    async def _wait_for_queue_or_stop(self) -> None:
        """Espera ativa enquanto a fila estiver vazia e o bot não for parado."""
        while not self.queue and not self._is_stopped:
            await asyncio.sleep(1.0)

    async def _announce_now_playing(self, track: Track) -> None:
        """Envia embed informativo sobre a faixa tocando no momento."""
        embed = discord.Embed(
            title="🎶 Tocando Agora",
            description=f"[{track.title}]({track.webpage_url})",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Duração", value=track.formatted_duration, inline=True)
        embed.add_field(name="Pedido por", value=track.requester, inline=True)
        if self.loop_mode != LoopMode.OFF:
            embed.add_field(name="Modo Loop", value=self.loop_mode.value.upper(), inline=True)
        if track.thumbnail:
            embed.set_thumbnail(url=track.thumbnail)

        try:
            await self.text_channel.send(embed=embed)  # type: ignore[union-attr]
        except Exception as e:
            logger.warning("Não foi possível enviar anúncio no canal: %s", e)

    async def _handle_inactivity_disconnect(self) -> None:
        """Desconecta o bot após tempo ocioso para liberar recursos."""
        vc = self.voice_client
        if vc and vc.is_connected():
            if self.text_channel:
                try:
                    await self.text_channel.send("⏱️ Fila vazia há 5 minutos. Desconectando do canal de voz...")
                except Exception:
                    pass
            await vc.disconnect()
        self._is_stopped = True

    def destroy(self) -> None:
        """Cancela tasks e encerra o player."""
        self.stop()
        if self._player_task and not self._player_task.done():
            self._player_task.cancel()
