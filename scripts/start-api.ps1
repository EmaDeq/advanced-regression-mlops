$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)
$python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) { throw 'First run setup.ps1 in the project root.' }
& $python -m uvicorn advanced_regression_mlops.api:app --host 127.0.0.1 --port 8000
