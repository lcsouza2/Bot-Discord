"""Cog de comandos gerais e utilitários."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class GeneralCog(commands.Cog, name="Geral"):
    """Comandos informativos e utilitários do bot."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="ping", description="Verifica a latência do bot.")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Responde com a latência atual em milissegundos."""
        latency_ms = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Latência do WebSocket: **{latency_ms} ms**",
            color=discord.Color.green(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ajuda", description="Lista todos os comandos disponíveis no bot.")
    async def ajuda(self, interaction: discord.Interaction) -> None:
        """Exibe o guia completo de comandos."""
        embed = discord.Embed(
            title="📖 Comandos do Bot de Música",
            description="Use os comandos de barra (`/`) para controlar a reprodução:",
            color=discord.Color.blurple(),
        )

        music_commands = (
            "`/play <busca_ou_link>` - Toca uma música ou playlist do YouTube/SoundCloud.\n"
            "`/pause` - Pausa a faixa que está tocando.\n"
            "`/resume` - Retoma a reprodução pausada.\n"
            "`/skip` - Pula para a próxima música da fila.\n"
            "`/queue` - Mostra as próximas músicas na fila do servidor.\n"
            "`/nowplaying` - Mostra detalhes da faixa atual.\n"
            "`/loop <modo>` - Define repetição (`off`, `track`, `queue`).\n"
            "`/volume <0-100>` - Ajusta o volume da reprodução.\n"
            "`/clear` - Limpa a lista de espera sem parar a música atual.\n"
            "`/stop` - Para a música, limpa a fila e sai do canal de voz."
        )

        general_commands = (
            "`/ping` - Mostra a latência do bot.\n"
            "`/ajuda` - Exibe esta mensagem de ajuda."
        )

        embed.add_field(name="🎵 Música", value=music_commands, inline=False)
        embed.add_field(name="⚙️ Geral", value=general_commands, inline=False)
        embed.set_footer(text="Bot desenvolvido com Python e discord.py")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Registra o cog no bot."""
    await bot.add_cog(GeneralCog(bot))
