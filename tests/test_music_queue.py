"""Testes unitários para a fila de música e modelos."""

from unittest.mock import MagicMock
import pytest
from src.music.models import LoopMode, Track
from src.music.player import GuildMusicPlayer


def test_track_duration_formatting():
    """Verifica formatação legível da duração da faixa."""
    track_live = Track("Live", "http://audio", "http://web", 0, "User")
    assert track_live.formatted_duration == "Ao vivo / Desconhecido"

    track_short = Track("Short", "http://audio", "http://web", 45, "User")
    assert track_short.formatted_duration == "00:45"

    track_medium = Track("Medium", "http://audio", "http://web", 215, "User")
    assert track_medium.formatted_duration == "03:35"

    track_long = Track("Long", "http://audio", "http://web", 3665, "User")
    assert track_long.formatted_duration == "01:01:05"


def test_loop_mode_parsing():
    """Verifica conversão segura de strings para LoopMode."""
    assert LoopMode.from_str("track") == LoopMode.TRACK
    assert LoopMode.from_str("TRACK") == LoopMode.TRACK
    assert LoopMode.from_str("queue") == LoopMode.QUEUE
    assert LoopMode.from_str("off") == LoopMode.OFF
    assert LoopMode.from_str("invalid_mode") == LoopMode.OFF


@pytest.fixture
def mock_player():
    """Fixture que cria um GuildMusicPlayer com bot e guild mockados."""
    bot = MagicMock()
    guild = MagicMock()
    guild.voice_client = None
    player = GuildMusicPlayer(bot, guild)
    # Evita disparar task assíncrona automática durante os testes síncronos
    player.start_if_needed = MagicMock()
    return player


def test_enqueue_and_clear(mock_player):
    """Verifica adição de faixas e limpeza da fila."""
    t1 = Track("Song 1", "http://1", "http://web1", 120, "User1")
    t2 = Track("Song 2", "http://2", "http://web2", 180, "User2")

    added = mock_player.enqueue([t1, t2])
    assert added == 2
    assert len(mock_player.queue) == 2
    assert mock_player.queue[0].title == "Song 1"

    cleared = mock_player.clear()
    assert cleared == 2
    assert len(mock_player.queue) == 0


def test_set_volume_clamping(mock_player):
    """Verifica limite de volume entre 0% e 200%."""
    assert mock_player.set_volume(0.8) == 0.8
    assert mock_player.set_volume(-0.5) == 0.0
    assert mock_player.set_volume(3.5) == 2.0


def test_skip_with_active_voice(mock_player):
    """Verifica que o skip interrompe o voice_client ativo."""
    vc = MagicMock()
    vc.is_playing.return_value = True
    mock_player.guild.voice_client = vc

    mock_player.loop_mode = LoopMode.TRACK
    result = mock_player.skip()

    assert result is True
    vc.stop.assert_called_once()
    # Pular manualmente no modo TRACK reseta para OFF para evitar loop infinito
    assert mock_player.loop_mode == LoopMode.OFF


def test_pause_and_resume(mock_player):
    """Verifica ações de pausar e despausar."""
    vc = MagicMock()
    vc.is_playing.return_value = True
    vc.is_paused.return_value = False
    mock_player.guild.voice_client = vc

    assert mock_player.pause() is True
    vc.pause.assert_called_once()

    vc.is_paused.return_value = True
    assert mock_player.resume() is True
    vc.resume.assert_called_once()
