@echo off
echo Starting PostgreSQL...
docker run -d --name opstool-postgres -e POSTGRES_DB=opstool -e POSTGRES_USER=opstool -e POSTGRES_PASSWORD=password -p 5432:5432 postgres:15-alpine

echo Starting Redis...
docker run -d --name opstool-redis -p 6379:6379 redis:7-alpine

echo Waiting for services to start...
timeout /t 10

echo Services started!
echo PostgreSQL: localhost:5432 (user: opstool, password: password, db: opstool)
echo Redis: localhost:6379
echo.
echo Run: go run ./cmd/server