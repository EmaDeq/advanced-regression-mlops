$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if ((& git branch --show-current).Trim() -ne 'main') {
    throw 'Final verification requires main.'
}
if (& git status --porcelain) { throw 'Working tree must be clean.' }

$dev = Get-Content '.\releases\dev.json' -Raw | ConvertFrom-Json
$prod = Get-Content '.\releases\prod.json' -Raw | ConvertFrom-Json
if ($dev.image -ne $prod.image) { throw 'DEV and PROD image digests differ.' }
if ($dev.release_run_id -ne $prod.release_run_id) { throw 'Release run IDs differ.' }
if ($dev.deployment_run_id -ne $prod.dev_deployment_run_id) {
    throw 'DEV deployment IDs differ.'
}
if ($prod.image -cnotmatch '^ghcr\.io/emadeq/advanced-regression-mlops@sha256:[a-f0-9]{64}$') {
    throw 'Not an immutable approved GHCR image.'
}

function Confirm-Run {
    param([long]$Id, [string]$Name)
    $r = & gh run view $Id --json conclusion,name,headBranch | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0 -or $r.conclusion -ne 'success' -or $r.name -ne $Name -or $r.headBranch -ne 'main') {
        throw "Required workflow run $Id is missing or unsuccessful."
    }
}
Confirm-Run ([long]$prod.release_run_id) 'Release Candidate - Verified Docker'
Confirm-Run ([long]$prod.dev_deployment_run_id) 'Deploy DEV - Verified GHCR Digest'
Confirm-Run ([long]$prod.prod_deployment_run_id) 'Promote DEV-verified image to PROD'

foreach ($environment in @('dev', 'prod')) {
    $url = "https://advanced-regression-mlops-$environment.onrender.com"
    $healthResponse = Invoke-WebRequest -Uri "$url/health" -UseBasicParsing -TimeoutSec 180
    $health = $healthResponse.Content | ConvertFrom-Json
    $model = Invoke-RestMethod "$url/model-info" -TimeoutSec 180
    if ($health.status -ne 'ok' -or $health.environment -ne $environment) {
        throw "Bad $environment health response"
    }
    if ($model.model_version -ne 'v0.1.0' -or $model.features.Count -ne 12) {
        throw "Bad $environment model-info response"
    }
    if ($healthResponse.Headers['X-Content-Type-Options'] -ne 'nosniff') {
        throw "$environment security header missing"
    }
    if ($healthResponse.Headers['Cache-Control'] -ne 'no-store') {
        throw "$environment cache header missing"
    }
    if (-not $healthResponse.Headers['X-Request-ID']) {
        throw "$environment request ID missing"
    }
    Write-Host "$environment HEALTHY with correct security headers" -ForegroundColor Green
}
Write-Host "MLOPS FINAL ACCEPTANCE PASSED!" -ForegroundColor Green
Write-Host "Immutable image: $($prod.image)"
Write-Host 'Inspect Render Logs for event=http_request manually, then suspend services when idle.'
