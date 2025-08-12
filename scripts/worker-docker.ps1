Param(
  [string]$ImageTag = "opstool/worker:latest",
  [string]$RedisHost = "host.docker.internal",
  [int]$HealthPort = 8081
)

$ErrorActionPreference = "Stop"

pushd $PSScriptRoot\..

try {
  docker --version | Out-Null
} catch {
  Write-Error "Docker is not installed or not in PATH."
  exit 1
}

Write-Host "Building worker image: $ImageTag"
docker build -f deployments/docker/Dockerfile.python -t $ImageTag .

Write-Host "Stopping previous container if exists..."
docker rm -f worker 2>$null | Out-Null

Write-Host "Running worker container on port $HealthPort with REDIS_HOST=$RedisHost"
docker run -d -p "$HealthPort:$HealthPort" --name worker -e WORKER_HEALTH_PORT=$HealthPort -e REDIS_HOST=$RedisHost $ImageTag | Out-Null

Start-Sleep -Seconds 3

$healthUrl = "http://localhost:$HealthPort/healthz"
$readyUrl = "http://localhost:$HealthPort/readyz"

Write-Host "Checking health: $healthUrl"
try {
  (Invoke-WebRequest -UseBasicParsing $healthUrl).StatusCode
} catch {
  Write-Warning "Health check failed: $_"
}

Write-Host "Checking readiness (requires reachable Redis at $RedisHost): $readyUrl"
try {
  (Invoke-WebRequest -UseBasicParsing $readyUrl).StatusCode
} catch {
  Write-Warning "Readiness check likely failed (no Redis reachable): $_"
}

popd
