"""Testes unitários para comandos utilitários e ofensas carinhosas do GeneralCog."""

import pytest
from src.cogs.general import CARINHOSAS_OFENSAS, format_carinhosa_roast


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
