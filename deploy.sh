#!/bin/bash

# Defina a versão dinamicamente
VERSION_TAG="3.0.1"

# Caminho para o arquivo settings.py
SETTINGS_FILE="/opt/pd-enem-dev/core/settings.py"

# Atualiza o APP_VERSION no settings.py
echo "Atualizando versão no settings.py para $VERSION_TAG"
sed -i "s/^APP_VERSION = .*/APP_VERSION = \"$VERSION_TAG\"/" $SETTINGS_FILE

# Confirma se a versão foi alterada
grep "APP_VERSION" $SETTINGS_FILE

# Faz o login no Docker Hub
docker login

# Build da imagem com a nova versão
echo "Build da imagem Docker com a versão $VERSION_TAG"
docker build --build-arg BUILD_VERSION=$VERSION_TAG -t pd-enem:$VERSION_TAG . || { echo "Erro no build da imagem"; exit 1; }

# Tag da imagem
docker tag pd-enem:$VERSION_TAG cosmeaf/pd-enem:$VERSION_TAG

# Push da imagem para o Docker Hub
docker push cosmeaf/pd-enem:$VERSION_TAG || { echo "Erro ao enviar a imagem para o Docker Hub"; exit 1; }

# Verifica se o container antigo existe e o remove
echo "Verificando se existe um container antigo"
if [ "$(docker ps -a | grep pd-enem)" ]; then
    echo "Parando e removendo container antigo"
    docker stop pd-enem
    docker rm -f pd-enem
else
    echo "Nenhum container antigo encontrado"
fi

# Verifica se a rede app-network existe, caso contrário, cria uma nova
echo "Verificando se a rede app-network existe"
if [ -z "$(docker network ls | grep app-network)" ]; then
    echo "Criando a rede app-network"
    docker network create --subnet=172.16.0.0/16 app-network || { echo "Erro ao criar a rede"; exit 1; }
else
    echo "Rede app-network já existe"
fi

# Verifica se o container do Celery existe e o remove, se necessário
echo "Verificando se existe um container Celery antigo"
if [ "$(docker ps -a | grep celery)" ]; then
    echo "Parando e removendo container Celery antigo"
    docker stop celery
    docker rm -f celery
else
    echo "Nenhum container Celery antigo encontrado"
fi

# Executa o contêiner do Celery
echo "Executando o contêiner do Celery"
docker run -d \
  --name celery \
  --hostname celery \
  --network app-network \
  --restart always \
  -e CELERY_BROKER_URL='redis://172.16.0.13:6379/0' \
  -e CELERY_RESULT_BACKEND='redis://172.16.0.13:6379/0' \
  -e CELERY_ACCEPT_CONTENT='json' \
  -e CELERY_TASK_SERIALIZER='json' \
  -e CELERY_RESULT_SERIALIZER='json' \
  -e CELERY_TIMEZONE='America/Sao_Paulo' \
  cosmeaf/pd-enem:$VERSION_TAG \
  celery -A pd-enem worker --loglevel=info || { echo "Erro ao executar o container Celery"; exit 1; }

# Executar o novo container com a versão atualizada
echo "Executando novo container com a versão $VERSION_TAG"
docker run -d \
  --name pd-enem \
  --hostname pd-enem \
  --network app-network \
  --restart always \
  -p 7000:7000 \
  -e APP_VERSION=$VERSION_TAG \
  cosmeaf/pd-enem:$VERSION_TAG || { echo "Erro ao executar o container"; exit 1; }

echo "Deploy concluído com a versão $VERSION_TAG"
