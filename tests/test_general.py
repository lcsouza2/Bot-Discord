"""Testes unitários para comandos utilitários e ofensas carinhosas do GeneralCog."""

import pytest
from src.cogs.general import (
    CARINHOSAS_OFENSAS,
    format_bully_message,
    format_carinhosa_roast,
)


def test_format_carinhosa_roast_friend():
    """Valida que o alvo comum recebe menção formatada e texto da lista."""
    target = "<@123456789>"
    author = "<@987654321>"
    roast = format_carinhosa_roast(target=target, author=author, is_self=False, is_bot=False)

    assert target in roast
    assert any(roast == template.format(target=target) for template in CARINHOSAS_OFENSAS)


def test_format_carinhosa_roast_self():
    """Valida resposta especial quando o usuário tenta escurraçar a si próprio."""
    target = "<@111111111>"
    author = "<@111111111>"
    roast = format_carinhosa_roast(target=target, author=author, is_self=True, is_bot=False)

    assert author in roast
    assert "autoestima" in roast.lower()
    assert "cara de pastel" in roast.lower()


def test_format_carinhosa_roast_bot():
    """Valida resposta do bot quando o usuário tenta escurraçar o próprio bot."""
    target = "<@999999999>"
    author = "<@123456789>"
    roast = format_carinhosa_roast(target=target, author=author, is_self=False, is_bot=True)

    assert author in roast
    assert "python 3.13" in roast.lower()
    assert "chatgpt" in roast.lower()


def test_format_bully_message_in_call_mute_success():
    """Valida bully com usuário na call e mute bem-sucedido."""
    target = "<@123456789>"
    author = "<@987654321>"
    msg = format_bully_message(target=target, author=author, in_call=True, mute_success=True)

    assert target in msg
    assert "mutado na call por 15 segundos" in msg.lower()
    assert "bunda mole" in msg.lower() or "chorão" in msg.lower()


def test_format_bully_message_in_call_mute_forbidden():
    """Valida bully com usuário na call e erro de permissão para mutar."""
    target = "<@123456789>"
    author = "<@987654321>"
    msg = format_bully_message(target=target, author=author, in_call=True, mute_forbidden=True)

    assert target in msg
    assert "não tenho permissão" in msg.lower()
    assert "bunda mole" in msg.lower() or "chorão" in msg.lower()


def test_format_bully_message_not_in_call():
    """Valida bully com usuário fora da call (fugiu da call)."""
    target = "<@123456789>"
    author = "<@987654321>"
    msg = format_bully_message(target=target, author=author, in_call=False)

    assert target in msg
    assert "call" in msg.lower()
    assert "bunda mole" in msg.lower() or "chorão" in msg.lower()


def test_format_bully_message_self():
    """Valida bully em si mesmo."""
    target = "<@111111111>"
    author = "<@111111111>"
    msg = format_bully_message(target=target, author=author, in_call=True, is_self=True)

    assert author in msg
    assert "masoquista" in msg.lower()
    assert "bunda mole" in msg.lower()


def test_format_bully_message_bot():
    """Valida bully direcionado ao bot."""
    target = "<@999999999>"
    author = "<@123456789>"
    msg = format_bully_message(target=target, author=author, in_call=True, is_bot=True)

    assert author in msg
    assert "tentando dar bully em mim" in msg.lower()
    assert "bunda mole" in msg.lower()

