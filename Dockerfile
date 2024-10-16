# Use uma imagem base oficial do Python
FROM python:3.11-slim

# Instalação de pacotes do sistema para manipulação de dados, imagens, PDFs, etc.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tesseract-ocr \
    poppler-utils \
    libreoffice \
    ghostscript \
    unoconv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Criação do diretório para o código do projeto
WORKDIR /app

# Copie os requisitos do Python para a imagem
COPY requirements.txt /app/

# Instalação dos pacotes do Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalação do pacote python-dotenv para lidar com variáveis de ambiente
RUN pip install python-dotenv

# Copie o código da aplicação para a imagem
COPY . /app/

# Configuração de variáveis de ambiente para segurança
ENV DJANGO_ENV=production \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# Criação do diretório de arquivos estáticos e mídia
RUN mkdir -p /var/www/pd-enem/static /var/www/pd-enem/media

# Configuração do limite de upload de arquivos no Django
ENV DJANGO_FILE_UPLOAD_MAX_MEMORY_SIZE=5242880

# Executa as migrações, coleta arquivos estáticos e inicia o servidor Gunicorn
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:7000 --workers 3 & celery -A core worker --loglevel=info & wait"]

# Configurações de rede
EXPOSE 7000
