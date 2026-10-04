# Imagem base oficial leve com Python 3.13
FROM python:3.13-slim

# Evita geração de arquivos .pyc e força saída direta para stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala ffmpeg e certificados necessários para streaming de áudio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 botuser

WORKDIR /app

# Copia dependências primeiro para aproveitar o cache de camadas do Docker
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código-fonte da aplicação
COPY src/ ./src/

# Altera propriedade para o usuário botuser
RUN chown -R botuser:botuser /app

USER botuser

# Comando de inicialização do bot
CMD ["python", "src/main.py"]
