"""Cog de comandos musicais com suporte a filas, playlists e controles de reprodução."""

from __future__ import annotations

from typing import Dict, Literal, Optional
import discord
from discord import app_commands
from discord.ext import commands

from src.music.models import LoopMode
from src.music.player import GuildMusicPlayer
from src.music.ytdl import YTDLSource


class MusicCog(commands.Cog, name="Música"):
    """Comandos para tocar músicas, gerenciar filas e playlists no Discord."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.players: Dict[int, GuildMusicPlayer] = {}

    def get_player(self, guild: discord.Guild) -> GuildMusicPlayer:
        """Recupera ou instancia o player associado ao servidor."""
        player = self.players.get(guild.id)
        if player is None:
            player = GuildMusicPlayer(self.bot, guild)
            self.players[guild.id] = player
        return player

    async def _ensure_voice(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        """Garante que o usuário e o bot estejam conectados a um canal de voz."""
        if not isinstance(interaction.user, discord.Member) or not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send(
                "❌ Você precisa estar conectado a um canal de voz para usar este comando.",
                ephemeral=True,
            )
            return None

        user_channel = interaction.user.voice.channel
        guild = interaction.guild
        if guild is None:
            return None

        voice_client: Optional[discord.VoiceClient] = guild.voice_client  # type: ignore[assignment]

        if voice_client is None:
            voice_client = await user_channel.connect()
        elif voice_client.channel != user_channel:
            await voice_client.move_to(user_channel)

        return voice_client

    @app_commands.command(name="play", description="Toca uma música ou playlist do YouTube/SoundCloud.")
    @app_commands.describe(query="Nome da música ou URL (vídeo ou playlist)")
    async def play(self, interaction: discord.Interaction, query: str) -> None:
        """Pesquisa e enfileira uma música ou playlist."""
        await interaction.response.defer()

        vc = await self._ensure_voice(interaction)
        if vc is None or interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        player.text_channel = interaction.channel

        try:
            tracks = await YTDLSource.extract_tracks(
                query=query,
                requester=interaction.user.display_name,
                loop=self.bot.loop,
            )
        except Exception as exc:
            await interaction.followup.send(
                f"❌ Erro ao buscar áudio: `{exc}`",
                ephemeral=True,
            )
            return

        if not tracks:
            await interaction.followup.send(
                "❌ Nenhuma faixa encontrada para a pesquisa fornecida.",
                ephemeral=True,
            )
            return

        player.enqueue(tracks)

        if len(tracks) > 1:
            embed = discord.Embed(
                title="📑 Playlist Adicionada à Fila",
                description=f"Foram adicionadas **{len(tracks)} faixas** à fila!",
                color=discord.Color.green(),
            )
            await interaction.followup.send(embed=embed)
        else:
            first_track = tracks[0]
            if player.current and player.current != first_track:
                position = len(player.queue)
                embed = discord.Embed(
                    title="➕ Adicionada à Fila",
                    description=f"[{first_track.title}]({first_track.webpage_url})\nPosição na fila: **#{position}**",
                    color=discord.Color.blue(),
                )
                embed.add_field(name="Duração", value=first_track.formatted_duration, inline=True)
                if first_track.thumbnail:
                    embed.set_thumbnail(url=first_track.thumbnail)
                await interaction.followup.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="▶️ Carregando Reprodução",
                    description=f"[{first_track.title}]({first_track.webpage_url})",
                    color=discord.Color.green(),
                )
                await interaction.followup.send(embed=embed)

    @app_commands.command(name="pause", description="Pausa a reprodução da música atual.")
    async def pause(self, interaction: discord.Interaction) -> None:
        """Pausa o áudio em reprodução."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        if player.pause():
            await interaction.response.send_message("⏸️ Música pausada com sucesso.")
        else:
            await interaction.response.send_message("⚠️ Nenhuma música está tocando no momento.", ephemeral=True)

    @app_commands.command(name="resume", description="Retoma a reprodução pausada.")
    async def resume(self, interaction: discord.Interaction) -> None:
        """Retoma a música pausada."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        if player.resume():
            await interaction.response.send_message("▶️ Reprodução retomada.")
        else:
            await interaction.response.send_message("⚠️ A música não está pausada.", ephemeral=True)

    @app_commands.command(name="skip", description="Pula para a próxima música da fila.")
    async def skip(self, interaction: discord.Interaction) -> None:
        """Pula a faixa atual."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        if player.skip():
            await interaction.response.send_message("⏭️ Faixa pulada!")
        else:
            await interaction.response.send_message("⚠️ Não há nenhuma faixa tocando para pular.", ephemeral=True)

    @app_commands.command(name="queue", description="Exibe a fila de músicas do servidor.")
    @app_commands.describe(pagina="Número da página da fila (padrão: 1)")
    async def queue(self, interaction: discord.Interaction, pagina: Optional[int] = 1) -> None:
        """Mostra as faixas presentes na fila."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        current = player.current
        queue_list = player.queue

        if not current and not queue_list:
            await interaction.response.send_message("📭 A fila está vazia no momento.")
            return

        page = max(1, pagina or 1)
        per_page = 10
        total_pages = max(1, (len(queue_list) + per_page - 1) // per_page)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_tracks = queue_list[start_idx:end_idx]

        embed = discord.Embed(
            title=f"🎶 Fila de Reprodução - {interaction.guild.name}",
            color=discord.Color.blurple(),
        )

        if current:
            embed.add_field(
                name="🔊 Tocando Agora",
                value=f"[{current.title}]({current.webpage_url}) (`{current.formatted_duration}`) | Pedido por: {current.requester}",
                inline=False,
            )

        if page_tracks:
            lines = []
            for idx, track in enumerate(page_tracks, start=start_idx + 1):
                lines.append(f"`{idx}.` [{track.title}]({track.webpage_url}) (`{track.formatted_duration}`) - {track.requester}")
            embed.add_field(name="📋 A Seguir", value="\n".join(lines), inline=False)
        elif queue_list:
            embed.add_field(name="📋 A Seguir", value="Nenhuma música nesta página.", inline=False)
        else:
            embed.add_field(name="📋 A Seguir", value="Nenhuma outra música na fila.", inline=False)

        total_duration_sec = sum(t.duration for t in queue_list if t.duration > 0)
        minutes, seconds = divmod(total_duration_sec, 60)
        hours, minutes = divmod(minutes, 60)
        duration_str = f"{hours}h {minutes}m" if hours else f"{minutes}m {seconds}s"

        embed.set_footer(
            text=f"Página {page}/{total_pages} | {len(queue_list)} músicas na fila ({duration_str}) | Loop: {player.loop_mode.value.upper()}"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Exibe informações da música tocando agora.")
    async def nowplaying(self, interaction: discord.Interaction) -> None:
        """Detalha a faixa em execução."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        current = player.current
        if not current:
            await interaction.response.send_message("🔇 Nenhuma música está tocando no momento.", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎶 Tocando Agora",
            description=f"[{current.title}]({current.webpage_url})",
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Duração", value=current.formatted_duration, inline=True)
        embed.add_field(name="Pedido por", value=current.requester, inline=True)
        embed.add_field(name="Volume", value=f"{int(player.volume * 100)}%", inline=True)
        embed.add_field(name="Modo de Loop", value=player.loop_mode.value.upper(), inline=True)
        if current.thumbnail:
            embed.set_thumbnail(url=current.thumbnail)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Define o modo de repetição de áudio.")
    @app_commands.describe(modo="Modo de repetição: off, track (música atual) ou queue (fila inteira)")
    async def loop(
        self,
        interaction: discord.Interaction,
        modo: Literal["off", "track", "queue"],
    ) -> None:
        """Altera a configuração de loop."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        chosen_mode = LoopMode.from_str(modo)
        player.set_loop_mode(chosen_mode)

        status_messages = {
            LoopMode.OFF: "➡️ Modo de repetição desativado.",
            LoopMode.TRACK: "🔂 Repetindo a música atual continuamente.",
            LoopMode.QUEUE: "🔁 Repetindo a fila inteira.",
        }

        await interaction.response.send_message(status_messages[chosen_mode])

    @app_commands.command(name="volume", description="Ajusta o volume do bot.")
    @app_commands.describe(nivel="Volume em porcentagem (0 a 100)")
    async def volume(self, interaction: discord.Interaction, nivel: app_commands.Range[int, 0, 100]) -> None:
        """Altera o volume da reprodução."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        normalized = nivel / 100.0
        player.set_volume(normalized)
        await interaction.response.send_message(f"🔊 Volume ajustado para **{nivel}%**.")

    @app_commands.command(name="clear", description="Limpa todas as músicas pendentes na fila.")
    async def clear(self, interaction: discord.Interaction) -> None:
        """Limpa a fila sem interromper a música atual."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        removed = player.clear()
        await interaction.response.send_message(f"🗑️ Foram removidas **{removed} músicas** da fila.")

    @app_commands.command(name="stop", description="Para a reprodução, limpa a fila e desconecta o bot.")
    async def stop(self, interaction: discord.Interaction) -> None:
        """Para a reprodução e desconecta do canal de voz."""
        if interaction.guild is None:
            return

        player = self.get_player(interaction.guild)
        player.stop()

        vc: Optional[discord.VoiceClient] = interaction.guild.voice_client  # type: ignore[assignment]
        if vc and vc.is_connected():
            await vc.disconnect()

        await interaction.response.send_message("⏹️ Reprodução encerrada e fila limpa.")


async def setup(bot: commands.Bot) -> None:
    """Registra o cog no bot."""
    await bot.add_cog(MusicCog(bot))
