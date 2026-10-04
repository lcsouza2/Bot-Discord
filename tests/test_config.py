"""Testes unitários para o módulo de configuração."""

import os
import pytest
from src.config import Config


def test_config_loads_valid_values(monkeypatch):
    """Verifica carregamento correto com variáveis válidas."""
    monkeypatch.setenv("DISCORD_TOKEN", "valid_secret_token_123")
    monkeypatch.setenv("COMMAND_PREFIX", "?")
    monkeypatch.setenv("GUILD_ID", "1234567890")

    cfg = Config.load()
    assert cfg.discord_token == "valid_secret_token_123"
    assert cfg.command_prefix == "?"
    assert cfg.guild_id == 1234567890


def test_config_defaults_prefix_and_guild_id(monkeypatch):
    """Verifica valores padrão de prefixo e guild_id opcional."""
    monkeypatch.setenv("DISCORD_TOKEN", "valid_secret_token_123")
    monkeypatch.delenv("COMMAND_PREFIX", raising=False)
    monkeypatch.delenv("GUILD_ID", raising=False)

    cfg = Config.load()
    assert cfg.discord_token == "valid_secret_token_123"
    assert cfg.command_prefix == "!"
    assert cfg.guild_id is None


def test_config_missing_token_raises_value_error(monkeypatch):
    """Verifica se ausência de DISCORD_TOKEN levanta ValueError."""
    monkeypatch.delenv("DISCORD_TOKEN", raising=False)
    with pytest.raises(ValueError, match="DISCORD_TOKEN não configurado"):
        Config.load()


def test_config_placeholder_token_raises_value_error(monkeypatch):
    """Verifica se token com valor placeholder levanta ValueError."""
    monkeypatch.setenv("DISCORD_TOKEN", "seu_token_aqui")
    with pytest.raises(ValueError, match="DISCORD_TOKEN não configurado"):
        Config.load()


def test_config_invalid_guild_id_raises_value_error(monkeypatch):
    """Verifica se GUILD_ID não numérico levanta ValueError."""
    monkeypatch.setenv("DISCORD_TOKEN", "valid_secret_token_123")
    monkeypatch.setenv("GUILD_ID", "nao_e_numero")
    with pytest.raises(ValueError, match="GUILD_ID inválido"):
        Config.load()
