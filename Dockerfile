FROM python:3.11-slim

# Definindo variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalando dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libstdc++6

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando o requirements.txt e instalando as dependências
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copiando o restante do código da aplicação para o contêiner
COPY . ./

# Comando para rodar a aplicação usando Gunicorn
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:$PORT"]
