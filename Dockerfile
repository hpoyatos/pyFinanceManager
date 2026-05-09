# Usa uma imagem Python leve
FROM python:3.12-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências do sistema necessárias para drivers de banco (se houver)
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements primeiro para aproveitar o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Variáveis de ambiente padrão (serão sobrescritas pelo K8s)
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# Porta que a aplicação usa
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "run.py"]
