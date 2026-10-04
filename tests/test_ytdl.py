"""Testes unitários para validação e extração restrita ao YouTube."""

from unittest.mock import MagicMock, patch
import pytest
from src.music.ytdl import YTDLSource, is_youtube_url


def test_is_youtube_url_valid_domains():
    """Valida que URLs legítimas do YouTube são aceitas."""
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/playlist?list=PL123456",
    ]
    for url in valid_urls:
        assert is_youtube_url(url) is True, f"Deveria ser aceito: {url}"


def test_is_youtube_url_rejects_external_domains():
    """Valida que URLs fora do YouTube são rejeitadas."""
    invalid_urls = [
        "https://soundcloud.com/artist/song",
        "https://open.spotify.com/track/123",
        "https://fakeyoutube.com/watch?v=123",
        "https://youtube.com.evil.com/video",
        "https://twitch.tv/streamer",
        "not_a_valid_url",
        "ftp://youtube.com/file",
    ]
    for url in invalid_urls:
        assert is_youtube_url(url) is False, f"Deveria ser rejeitado: {url}"


@pytest.mark.asyncio
async def test_extract_tracks_rejects_non_youtube_url():
    """Verifica que links de outras plataformas levantam ValueError."""
    with pytest.raises(ValueError, match="Apenas links do YouTube"):
        await YTDLSource.extract_tracks("https://soundcloud.com/artist/track", requester="TestUser")


@pytest.mark.asyncio
async def test_extract_tracks_rejects_non_youtube_extractor():
    """Verifica que extratores fora do YouTube são rejeitados."""
    fake_data = {
        "extractor_key": "Soundcloud",
        "title": "Some soundcloud track",
        "url": "http://audio.stream",
    }
    with patch("src.music.ytdl.ytdl.extract_info", return_value=fake_data):
        with pytest.raises(ValueError, match="A fonte extraída não pertence ao YouTube"):
            await YTDLSource.extract_tracks("termo de busca", requester="TestUser")


@pytest.mark.asyncio
async def test_extract_tracks_successful_youtube():
    """Verifica extração correta de dados do YouTube."""
    fake_data = {
        "extractor_key": "Youtube",
        "title": "Música Teste",
        "url": "https://rr1---sn.googlevideo.com/videoplayback?...",
        "webpage_url": "https://www.youtube.com/watch?v=test",
        "duration": 210,
        "thumbnail": "https://i.ytimg.com/vi/test/hqdefault.jpg",
    }
    with patch("src.music.ytdl.ytdl.extract_info", return_value=fake_data):
        tracks = await YTDLSource.extract_tracks("https://www.youtube.com/watch?v=test", requester="TestUser")
        assert len(tracks) == 1
        assert tracks[0].title == "Música Teste"
        assert tracks[0].formatted_duration == "03:30"
        assert tracks[0].requester == "TestUser"
