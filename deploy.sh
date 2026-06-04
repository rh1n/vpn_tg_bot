#!/bin/bash
# deploy.sh

set -e

echo "Starting deployment..."

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Проверка наличия docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Копирование .env.example в .env если не существует
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example"
    cp .env.example .env
    echo "Please edit .env file with your configuration and run this script again."
    exit 1
fi

# Остановка текущих контейнеров
echo "Stopping existing containers..."
docker-compose down

# Сборка и запуск контейнеров
echo "Building and starting containers..."
docker-compose up -d --build

# Ожидание запуска базы данных
echo "Waiting for database to be ready..."
sleep 10

# Запуск миграций
echo "Running database migrations..."
docker-compose exec bot alembic upgrade head

echo "Deployment completed successfully!"
echo "Make sure to check the logs: docker-compose logs -f bot"
