"""Integração assíncrona com yt-dlp e criação de streams de áudio com FFmpeg."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List
import discord
import yt_dlp

from src.music.models import Track

# Opções de configuração para o yt-dlp
YTDL_FORMAT_OPTIONS: Dict[str, Any] = {
    "format": "bestaudio/best",
    "extractaudio": True,
    "audioformat": "mp3",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": False,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
}

# Opções para o FFmpeg com reconexão automática em caso de instabilidade na rede
FFMPEG_OPTIONS: Dict[str, str] = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}

ytdl = yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)


class YTDLSource:
    """Gerencia a extração assíncrona de metadados e conversão para fontes de áudio."""

    @classmethod
    async def extract_tracks(
        cls, query: str, requester: str, loop: asyncio.AbstractEventLoop | None = None
    ) -> List[Track]:
        """Extrai uma ou múltiplas faixas de forma não bloqueante.

        Suporta links diretos do YouTube/SoundCloud, pesquisas textuais e playlists.
        """
        active_loop = loop or asyncio.get_running_loop()

        def _extract() -> Dict[str, Any]:
            return ytdl.extract_info(query, download=False)

        # Executa em thread separada para não travar o loop de eventos do Discord
        data = await active_loop.run_in_executor(None, _extract)

        if not data:
            return []

        tracks: List[Track] = []

        if "entries" in data and data["entries"]:
            # Trata-se de uma playlist ou resultado de pesquisa
            for entry in data["entries"]:
                if entry:
                    track = cls._create_track_from_info(entry, requester)
                    if track:
                        tracks.append(track)
        else:
            # Vídeo / áudio individual
            track = cls._create_track_from_info(data, requester)
            if track:
                tracks.append(track)

        return tracks

    @classmethod
    def _create_track_from_info(cls, info: Dict[str, Any], requester: str) -> Track | None:
        """Converte dicionário de metadados do yt-dlp em uma instância de Track."""
        source_url = info.get("url")
        if not source_url:
            return None

        title = info.get("title", "Áudio Desconhecido")
        webpage_url = info.get("webpage_url") or info.get("url") or ""
        duration = int(info.get("duration") or 0)
        thumbnail = info.get("thumbnail")

        return Track(
            title=title,
            source_url=source_url,
            webpage_url=webpage_url,
            duration=duration,
            requester=requester,
            thumbnail=thumbnail,
        )

    @classmethod
    def create_audio_source(
        cls, track: Track, volume: float = 1.0
    ) -> discord.PCMVolumeTransformer:
        """Gera uma fonte de áudio discord.py PCMVolumeTransformer a partir do stream."""
        raw_source = discord.FFmpegPCMAudio(
            track.source_url,
            before_options=FFMPEG_OPTIONS["before_options"],
            options=FFMPEG_OPTIONS["options"],
        )
        return discord.PCMVolumeTransformer(raw_source, volume=volume)
