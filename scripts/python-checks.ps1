Param(
  [switch]$SkipInstall
)

Write-Host "Running Python checks (install deps, pytest, ruff, flake8)..."
$ErrorActionPreference = "Stop"

pushd $PSScriptRoot
try {
  python --version | Out-Null
  pip --version | Out-Null
} catch {
  Write-Error "Python or pip is not installed or not in PATH."
  exit 1
}

if (-not $SkipInstall) {
  Write-Host "Installing Python dependencies..."
  pip install -r requirements.txt
}

try {
  Write-Host "pytest"
  python -m pytest

  Write-Host "ruff check ."
  ruff check .

  Write-Host "flake8 ."
  flake8 .

  Write-Host "Python checks completed successfully."
} catch {
  Write-Error "Python checks failed: $_"
  exit 1
} finally {
  popd
}
