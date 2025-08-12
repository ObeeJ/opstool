@echo off
echo Starting OPSTOOL Quick Setup...

echo 1. Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 30

echo 2. Starting PostgreSQL and Redis...
docker run -d --name opstool-postgres -e POSTGRES_DB=opstool -e POSTGRES_USER=opstool -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine

docker run -d --name opstool-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes

echo 3. Installing Python dependencies (simplified)...
cd scripts
pip install redis requests psutil
cd ..

echo 4. Building Go application...
go build -o bin\opstool-server .\cmd\server

echo 5. Creating database schema...
timeout /t 10
echo CREATE TABLE IF NOT EXISTS tasks (id VARCHAR(255) PRIMARY KEY, name VARCHAR(255), type VARCHAR(50), status VARCHAR(50) DEFAULT 'created'); | docker exec -i opstool-postgres psql -U opstool -d opstool

echo 6. Starting OPSTOOL server...
set REDIS_HOST=localhost
set DB_HOST=localhost
set DB_USER=opstool
set DB_PASSWORD=password
set DB_NAME=opstool
bin\opstool-server.exe

pause