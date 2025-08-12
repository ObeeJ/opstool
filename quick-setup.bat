@echo off
echo Starting OPSTOOL Quick Setup...

echo 1. Starting Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
timeout /t 30

echo 2. Starting PostgreSQL and Redis...
docker run -d --name opstool-postgres -e POSTGRES_DB=opstool -e POSTGRES_USER=opstool -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine

docker run -d --name opstool-redis -p 6379:6379 redis:7-alpine redis-server --appendonly yes

echo 3. Installing Python dependencies...
cd scripts
pip install -r requirements.txt
cd ..

echo 4. Building Go application...
go build -o bin\opstool-server .\cmd\server

echo 5. Creating database schema...
timeout /t 10
docker cp migrations\001_initial.sql opstool-postgres:/001_initial.sql
docker exec -i opstool-postgres psql -U opstool -d opstool -f /001_initial.sql

echo 6. Starting OPSTOOL server...
set REDIS_HOST=localhost
set DB_HOST=localhost
set DB_USER=opstool
set DB_PASSWORD=password
set DB_NAME=opstool
bin\opstool-server.exe

pause