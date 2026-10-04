"""Ponto de entrada do Bot de Música Discord."""

from __future__ import annotations

import asyncio
import logging
import sys
import discord
from discord.ext import commands

from src.config import Config

# Configuração de logging estruturado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("bot")


class MusicBot(commands.Bot):
    """Cliente do bot de música com carregamento dinâmico de extensões."""

    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True

        super().__init__(
            command_prefix=config.command_prefix,
            intents=intents,
            help_command=None,
        )
        self.config = config

    async def setup_hook(self) -> None:
        """Carrega os cogs e sincroniza os comandos de barra (Slash Commands)."""
        logger.info("Carregando extensões...")
        initial_extensions = [
            "src.cogs.general",
            "src.cogs.music",
        ]

        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info("Extensão carregada: %s", ext)
            except Exception as exc:
                logger.error("Falha ao carregar extensão %s: %s", ext, exc, exc_info=True)

        # Sincronização dos comandos de barra
        if self.config.guild_id:
            guild_obj = discord.Object(id=self.config.guild_id)
            self.tree.copy_global_to(guild=guild_obj)
            synced = await self.tree.sync(guild=guild_obj)
            logger.info(
                "Sincronizados %d comandos slash para o servidor de desenvolvimento (Guild ID: %s)",
                len(synced),
                self.config.guild_id,
            )
        else:
            synced = await self.tree.sync()
            logger.info("Sincronizados %d comandos slash globalmente", len(synced))

    async def on_ready(self) -> None:
        """Callback invocado quando o bot estabelece conexão com o gateway do Discord."""
        logger.info("===============================================")
        logger.info("Bot online com sucesso!")
        logger.info("Usuário: %s (ID: %s)", self.user, self.user.id if self.user else "N/A")
        logger.info("Servidores conectados: %d", len(self.guilds))
        logger.info("===============================================")

        # Define o status / presença do bot
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name="/play | Músicas e Playlists",
        )
        await self.change_presence(activity=activity, status=discord.Status.online)


def main() -> None:
    """Carrega as configurações e inicializa a execução do bot."""
    try:
        config = Config.load()
    except ValueError as err:
        logger.error("Erro de configuração: %s", err)
        sys.exit(1)

    bot = MusicBot(config)

    try:
        bot.run(config.discord_token, log_handler=None)
    except discord.LoginFailure:
        logger.error("Falha no login: O token fornecido no .env é inválido.")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot finalizado pelo usuário.")


if __name__ == "__main__":
    main()
