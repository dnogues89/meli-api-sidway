#!/bin/bash
echo "inicio de build"

echo "Cambio directorio app"
cd /opt/meli-api-sidway/images

echo "Mato docker instance"
docker compose down
docker system prune -f
cd ..

echo "Pull de Github"
git pull

echo "Build instancia docker"
docker build -t meli-api-sidway:v1 .
cd images

echo "Inicio instancia docker"
docker compose up -d
