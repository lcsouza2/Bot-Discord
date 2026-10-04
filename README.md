# 🎵 Discord Music Bot (Python)

Bot de música modular para Discord desenvolvido em Python utilizando [`discord.py`](https://discordpy.readthedocs.io/), [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) e `FFmpeg`.

---

## 🚀 Funcionalidades

- **Comandos de Barra Modernos (Slash Commands)**: Suporte completo à interface nativa do Discord.
- **Exclusividade YouTube**: Reprodução restrita a vídeos, buscas textuais e playlists do YouTube (`youtube.com` e `youtu.be`).
- **Filas e Playlists**: Suporte para enfileirar vídeos individuais ou playlists completas do YouTube.
- **Reprodução Não-Bloqueante**: Extração de metadados em threads assíncronas para não travar o heartbeat do bot.
- **Modos de Loop**: Repetição da música atual (`track`), repetição da fila inteira (`queue`) ou desativado (`off`).
- **Controle Total de Reprodução**: Pausar, retomar, pular (skip), ajustar volume e limpar fila.
- **Desconexão por Inatividade**: O bot libera recursos desconectando-se automaticamente após 5 minutos de ociosidade.

---

## 📋 Pré-requisitos

1. **Python 3.10+** (testado e validado em Python 3.13)
2. **FFmpeg** instalado no sistema operacional:
   ```bash
   # Ubuntu / Debian
   sudo apt update && sudo apt install -y ffmpeg

   # Fedora
   sudo dnf install -y ffmpeg

   # Arch Linux
   sudo pacman -S ffmpeg
   ```

---

## 🛠️ Passo a Passo: Configuração do Bot no Discord

### 1. Criar Aplicação no Discord Developer Portal
1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications).
2. Clique em **"New Application"** e dê um nome ao seu bot.
3. No menu lateral esquerdo, vá em **"Bot"**:
   - Clique em **"Reset Token"** e copie o seu **Token secreto**.
   - Na seção **"Privileged Gateway Intents"**, ative:
     - ✅ **Message Content Intent**
     - ✅ **Server Members Intent** (opcional, para boas-vindas)

### 2. Gerar Link de Convite (OAuth2)
1. No menu lateral, acesse **"OAuth2" -> "URL Generator"**.
2. Em **Scopes**, selecione:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Em **Bot Permissions**, selecione:
   - ✅ `Send Messages`
   - ✅ `Embed Links`
   - ✅ `Connect`
   - ✅ `Speak`
   - ✅ `Use Application Commands`
4. Copie a URL gerada no final da página e abra-a no navegador para adicionar o bot ao seu servidor do Discord.

---

## 💻 Instalação e Execução Local

### 1. Clonar repositório e criar ambiente virtual:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar variáveis de ambiente:
Crie seu arquivo `.env` a partir do modelo:
```bash
cp .env.example .env
```
Edite o arquivo `.env` com seu editor preferido:
```ini
DISCORD_TOKEN=coloque_aqui_o_token_do_seu_bot
COMMAND_PREFIX=!
# Dica: adicione o ID do seu servidor de testes abaixo para que os Slash Commands
# apareçam instantaneamente, sem aguardar a propagação global do Discord:
GUILD_ID=
```

### 3. Rodar os testes automatizados:
```bash
pytest -v tests/
```

### 4. Iniciar o bot:
```bash
python3 src/main.py
```

---

## 🎶 Lista de Comandos (/Slash Commands)

| Comando | Descrição |
| :--- | :--- |
| `/play <query>` | Toca uma música ou adiciona uma playlist inteira do YouTube à fila do servidor. |
| `/pause` | Pausa a reprodução da música atual. |
| `/resume` | Retoma a reprodução pausada. |
| `/skip` | Pula para a próxima música da lista de espera. |
| `/queue [pagina]` | Exibe a lista de faixas na fila de reprodução paginada. |
| `/nowplaying` | Mostra detalhes da faixa tocando agora (título, autor, duração, etc). |
| `/loop <off \| track \| queue>` | Altera o modo de repetição de áudio. |
| `/volume <0-100>` | Altera o volume do áudio. |
| `/clear` | Remove todas as faixas pendentes da fila sem parar a atual. |
| `/stop` | Interrompe o áudio, limpa a fila e desconecta do canal de voz. |
| `/ping` | Mede e exibe a latência WebSocket do bot. |
| `/ajuda` | Mostra o guia rápido com todos os comandos disponíveis. |

---

## 🏛️ Estrutura do Projeto

```
bot-discord/
├── .env.example            # Exemplo das variáveis de ambiente
├── requirements.txt        # Dependências (discord.py, yt-dlp, etc.)
├── README.md               # Documentação completa
├── src/
│   ├── config.py           # Validação e carregamento de configurações
│   ├── main.py             # Entrada principal e registro de Slash Commands
│   ├── cogs/
│   │   ├── general.py      # Comandos utilitários (/ping, /ajuda)
│   │   └── music.py        # Comandos de reprodução e gerenciamento de voz
│   └── music/
│       ├── models.py       # Dataclasses de Track e Enum LoopMode
│       ├── player.py       # Gerenciador de fila e player de cada servidor
│       └── ytdl.py         # Extração não-bloqueante com yt-dlp e stream FFmpeg
└── tests/
    ├── test_config.py      # Testes de variáveis de ambiente
    └── test_music_queue.py # Testes da fila de reprodução e modelos
```
