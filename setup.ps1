<#
.SYNOPSIS
  Set up Python, install packages, test, and train. No cloud account/payment needed.
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -SkipTraining
#>
param([switch]$SkipTraining)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

function Check-Exit([string]$step) {
    if ($LASTEXITCODE -ne 0) { throw "$step failed (exit code $LASTEXITCODE)" }
}

Write-Host '=== Advanced Regression MLOps: Windows bootstrap ===' -ForegroundColor Cyan
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.12 --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw 'Python 3.12 launcher not found. Install: winget install --id Python.Python.3.12 -e'
    }
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        & py -3.12 -m venv .venv
        Check-Exit 'Create virtual environment'
    }
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python --version
    & python -c "import sys; assert sys.version_info[:2] == (3,12), 'Install Python 3.12'"
    Check-Exit 'Validate Python version'
    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        & python -m venv .venv
        Check-Exit 'Create virtual environment'
    }
} else {
    throw 'Install Python 3.12 first: winget install --id Python.Python.3.12 -e'
}

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
Write-Host 'Installing dependencies to the private .venv (no global Python changes)...' -ForegroundColor Cyan
& $python -m pip install --upgrade pip
Check-Exit 'Upgrade local pip'
& $python -m pip install -e '.[dev]'
Check-Exit 'Install project'
& $python -m ruff format .
Check-Exit 'Ruff autoformat'
& $python -m ruff check .
Check-Exit 'Ruff lint'
& $python -m ruff format --check .
Check-Exit 'Ruff formatting'
& $python -m pytest -q
Check-Exit 'Unit tests'

if (-not $SkipTraining) {
    Write-Host 'Fetching historical Boston data (if missing) and training model...' -ForegroundColor Cyan
    & $python -m advanced_regression_mlops.train --n-iter 6
    Check-Exit 'Model training'
}
if (Get-Command git -ErrorAction SilentlyContinue) {
    if (-not (Test-Path '.git')) {
        & git init -b main
        Check-Exit 'Initialize Git repository'
    }
} else {
    Write-Warning 'Git not installed. Run: winget install --id Git.Git -e'
}
Write-Host ''
Write-Host 'Ready! To start API: .\scripts\start-api.ps1' -ForegroundColor Green
Write-Host 'Test it in a second terminal: .\scripts\smoke-test.ps1'
Write-Host 'API documentation: http://127.0.0.1:8000/docs'
