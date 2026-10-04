"""Testes unitários para o comando de punição (/punish) e canal punishing."""

from unittest.mock import AsyncMock, MagicMock
import discord
import pytest
from src.cogs.music import _get_or_create_punish_channel, format_punish_message


def test_format_punish_message_bot():
    """Valida tentativa de punir o bot."""
    msg = format_punish_message("<@bot>", "<@user>", is_bot=True)
    assert "tentando punir o bot" in msg.lower()
    assert "<@user>" in msg


def test_format_punish_message_self():
    """Valida auto-punição."""
    msg = format_punish_message(
        "<@user>", "<@user>", is_self=True, track_title="Skibidi Toilet"
    )
    assert "voluntariamente" in msg.lower()
    assert "skibidi toilet" in msg.lower()


def test_format_punish_message_moved():
    """Valida punição aplicada com usuário movido para a call punishing."""
    msg = format_punish_message(
        target="<@victim>",
        author="<@user>",
        moved=True,
        in_call=True,
        track_title="Crazy Frog",
    )
    assert "<@victim>" in msg
    assert "arrastado para o canal **punishing**" in msg
    assert "crazy frog" in msg.lower()


def test_format_punish_message_move_forbidden():
    """Valida punição parcial quando falta permissão para mover."""
    msg = format_punish_message(
        target="<@victim>",
        author="<@user>",
        moved=False,
        in_call=True,
        error_move="Permissão negada",
        track_title="Baby Shark",
    )
    assert "punição parcial" in msg.lower()
    assert "baby shark" in msg.lower()


def test_format_punish_message_not_in_call():
    """Valida punição quando o usuário nem na call está."""
    msg = format_punish_message(
        target="<@victim>",
        author="<@user>",
        moved=False,
        in_call=False,
        track_title="Gummy Bear",
    )
    assert "condenado ausente" in msg.lower()
    assert "gummy bear" in msg.lower()


@pytest.mark.asyncio
async def test_get_or_create_punish_channel_existing():
    """Verifica que reaproveita canal 'punishing' existente."""
    guild = MagicMock()
    existing_ch = MagicMock()
    existing_ch.name = "punishing"
    guild.voice_channels = [existing_ch]

    ch, err = await _get_or_create_punish_channel(guild)
    assert ch == existing_ch
    assert err is None
    guild.create_voice_channel.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_punish_channel_create_new():
    """Verifica criação de canal quando 'punishing' não existe."""
    guild = MagicMock()
    guild.voice_channels = []
    created_ch = MagicMock()
    guild.create_voice_channel = AsyncMock(return_value=created_ch)

    ch, err = await _get_or_create_punish_channel(guild)
    assert ch == created_ch
    assert err is None
    guild.create_voice_channel.assert_called_once_with(
        "punishing", reason="Canal criado para o comando /punish"
    )


@pytest.mark.asyncio
async def test_get_or_create_punish_channel_forbidden():
    """Verifica tratamento de erro quando falta permissão para criar canal."""
    guild = MagicMock()
    guild.voice_channels = []
    guild.create_voice_channel = AsyncMock(
        side_effect=discord.Forbidden(MagicMock(), "Sem permissão")
    )

    ch, err = await _get_or_create_punish_channel(guild)
    assert ch is None
    assert "gerenciar canais" in err.lower()


def test_brainrot_songs_contains_required_tracks():
    """Valida presença das faixas obrigatórias de brainrot."""
    from src.cogs.music import BRAINROT_SONGS

    assert "Moranguete abacatudo 67 42" in BRAINROT_SONGS
    assert "rap do tung tung sahur" in BRAINROT_SONGS
    assert "brainrot song" in BRAINROT_SONGS
    assert len(BRAINROT_SONGS) >= 10
