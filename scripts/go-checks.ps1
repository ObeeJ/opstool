Param(
  [switch]$VerboseMode
)

Write-Host "Running Go checks (tidy, build, test)..."
$ErrorActionPreference = "Stop"

pushd $PSScriptRoot\..
try {
  go version | Out-Null
} catch {
  Write-Error "Go is not installed or not in PATH."
  exit 1
}

try {
  Write-Host "go mod tidy"
  go mod tidy

  Write-Host "go build ./..."
  go build ./...

  Write-Host "go test ./..."
  go test ./...

  Write-Host "Go checks completed successfully."
} catch {
  Write-Error "Go checks failed: $_"
  exit 1
} finally {
  popd
}
