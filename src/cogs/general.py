"""Cog de comandos gerais e utilitários."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


import random

CARINHOSAS_OFENSAS = [
    "{target}, você tem a agilidade cognitiva de uma tartaruga de patins na subida, seu projeto inacabado de gente!",
    "Olha aqui {target}, você é o tipo de pessoa que tropeça no cabo do Wi-Fi e pede desculpa pro modem, seu pamonha!",
    "{target}, sua cabeça parece um balão de festa junina: brilhante por fora e cheia de vento por dentro, seu cabeçudo!",
    "{target}, se besteira pagasse imposto, você já teria falido três continentes sozinho, seu indivíduo desprovido de bateria social!",
    "{target}, você é tão desligado que se cair uma chuva de dinheiro, você sai na rua de guarda-chuva aberto, seu abestado!",
    "{target}, você tem o carisma de um tijolo baiano úmido, mas a gente ainda te atura porque você tem um bom coração, seu pastel de vento!",
    "{target}, você é mais confuso que cachorro em dia de mudança, seu saco de batatas ambulante!",
    "{target}, você é o motivo pelo qual o shampoo vem com manual de instruções no verso, seu espirro de poeira!",
    "{target}, você é uma pessoa nota 10... numa escala que vai até 1000, seu cabeça de pudim!",
    "{target}, se a preguiça fosse esporte olímpico, você não ganhava nem medalha só pra não ter que subir no pódio, seu comediante!",
    "{target}, você tem a sutileza de um rinoceronte jogando xadrez, sua aberração adorável!",
    "{target}, às vezes eu acho que você pensa, mas aí você fala e me prova o contrário, seu pedaço de mau caminho!",
]


def format_carinhosa_roast(target: str, author: str, is_self: bool = False, is_bot: bool = False) -> str:
    """Gera uma ofensa carinhosa apropriada de acordo com o alvo."""
    if is_bot:
        return (
            f"Tentando me escurraçar, {author}? Eu rodo em Python 3.13 assíncrono com yt-dlp e FFmpeg, "
            "e você não aguenta nem compilar um 'olá mundo' sem pedir socorro pro ChatGPT, seu comédia!"
        )
    if is_self:
        return (
            f"Querendo se escurraçar sozinho, {author}? A autoestima tá tão no subsolo assim, "
            "seu projeto de derrotado? Vai tomar uma água e lavar essa cara de pastel!"
        )
    template = random.choice(CARINHOSAS_OFENSAS)
    return template.format(target=target)


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

    @app_commands.command(name="escurraçar", description="Profere uma ofensa carinhosa e bem-humorada a um usuário.")
    @app_commands.describe(usuario="O usuário que você deseja escurraçar carinhosamente")
    async def escurracar(self, interaction: discord.Interaction, usuario: discord.Member) -> None:
        """Envia uma ofensa carinhosa e engraçada marcando o membro escolhido."""
        bot_user = self.bot.user
        is_bot = bot_user is not None and usuario.id == bot_user.id
        is_self = usuario.id == interaction.user.id

        message = format_carinhosa_roast(
            target=usuario.mention,
            author=interaction.user.mention,
            is_self=is_self,
            is_bot=is_bot,
        )

        embed = discord.Embed(
            title="💥 Escurrançamento Carinhoso!",
            description=message,
            color=discord.Color.orange(),
        )
        embed.set_footer(text=f"Desferido por {interaction.user.display_name} • Com amor ❤️")

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
            "`/play <busca_ou_link>` - Toca uma música ou playlist do YouTube (vídeo, playlist ou busca).\n"
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
            "`/escurraçar <usuario>` - Profere ofensas carinhosas a um amigo.\n"
            "`/ajuda` - Exibe esta mensagem de ajuda."
        )

        embed.add_field(name="🎵 Música", value=music_commands, inline=False)
        embed.add_field(name="⚙️ Geral e Diversão", value=general_commands, inline=False)
        embed.set_footer(text="Bot desenvolvido com Python e discord.py")

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Registra o cog no bot."""
    await bot.add_cog(GeneralCog(bot))
