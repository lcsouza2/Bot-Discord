"""Módulo de configuração do bot via variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env se presente
load_dotenv()


@dataclass(frozen=True)
class Config:
    """Configurações da aplicação."""

    discord_token: str
    command_prefix: str = "!"
    guild_id: Optional[int] = None

    @classmethod
    def load(cls) -> Config:
        """Carrega e valida as configurações de ambiente.

        Raises:
            ValueError: Se DISCORD_TOKEN não estiver configurado ou for o valor padrão.
        """
        token = os.getenv("DISCORD_TOKEN", "").strip()
        if not token or token == "seu_token_aqui":
            raise ValueError(
                "DISCORD_TOKEN não configurado! "
                "Crie um arquivo .env baseado no .env.example e adicione o token do bot."
            )

        prefix = os.getenv("COMMAND_PREFIX", "!").strip() or "!"

        raw_guild_id = os.getenv("GUILD_ID", "").strip()
        guild_id: Optional[int] = None
        if raw_guild_id:
            try:
                guild_id = int(raw_guild_id)
            except ValueError:
                raise ValueError(f"GUILD_ID inválido: '{raw_guild_id}' deve ser um número inteiro.")

        return cls(
            discord_token=token,
            command_prefix=prefix,
            guild_id=guild_id,
        )
