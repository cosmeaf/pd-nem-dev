#!/bin/bash

# Defina a versão dinamicamente
VERSION_TAG="2.0.0"

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
