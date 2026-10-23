param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'prod')]
    [string]$Environment,

    [Parameter(Mandatory = $true)]
    [long]$DeployRunId,

    [long]$ReleaseRunId = 0
)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $PSScriptRoot)

if ((& git branch --show-current).Trim() -ne 'main') {
    throw 'Start on main.'
}
& git pull --ff-only origin main
if ($LASTEXITCODE -ne 0) { throw 'git pull failed' }
if (& git status --porcelain) { throw 'Commit or stash changes first.' }

function Confirm-Run {
    param([long]$Id, [string]$ExpectedName)
    $record = & gh run view $Id --json conclusion,name,headBranch | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0) { throw "Cannot inspect workflow $Id" }
    if ($record.conclusion -ne 'success' -or $record.name -ne $ExpectedName -or $record.headBranch -ne 'main') {
        throw "Wrong or unsuccessful workflow $Id"
    }
}

$branch = "feature/record-final-$Environment-$DeployRunId"
$utf8 = New-Object System.Text.UTF8Encoding($false)
$timestamp = (Get-Date).ToUniversalTime().ToString('o')
$devPath = Join-Path (Get-Location).Path 'releases\dev.json'
$prodPath = Join-Path (Get-Location).Path 'releases\prod.json'
$dev = Get-Content $devPath -Raw | ConvertFrom-Json
$prod = Get-Content $prodPath -Raw | ConvertFrom-Json

if ($Environment -eq 'dev') {
    if ($ReleaseRunId -le 0) { throw 'DEV requires -ReleaseRunId.' }
    Confirm-Run $ReleaseRunId 'Release Candidate - Verified Docker'
    Confirm-Run $DeployRunId 'Deploy DEV - Verified GHCR Digest'

    $temp = Join-Path $env:TEMP ("release-digest-" + [guid]::NewGuid())
    New-Item -ItemType Directory $temp -Force | Out-Null
    try {
        & gh run download $ReleaseRunId --name "image-digest-$ReleaseRunId" --dir $temp
        if ($LASTEXITCODE -ne 0) { throw 'Cannot download release digest artifact.' }
        $image = (Get-Content (Join-Path $temp 'image-digest.txt') -Raw).Trim()
    }
    finally {
        Remove-Item $temp -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($image -cnotmatch '^ghcr\.io/emadeq/advanced-regression-mlops@sha256:[a-f0-9]{64}$') {
        throw 'Invalid image reference.'
    }
    if ($image -eq $dev.image) { throw 'DEV already references this image.' }
    $new = [ordered]@{
        environment = 'dev'
        image = $image
        release_run_id = $ReleaseRunId
        deployment_run_id = $DeployRunId
        api_url = $dev.api_url
        model_version = $dev.model_version
        recorded_at_utc = $timestamp
    }
    & git switch -c $branch
    if ($LASTEXITCODE -ne 0) { throw 'Could not create branch.' }
    [System.IO.File]::WriteAllText($devPath, (($new | ConvertTo-Json -Depth 10) + "`n"), $utf8)
}
else {
    Confirm-Run $DeployRunId 'Promote DEV-verified image to PROD'
    Confirm-Run ([long]$dev.release_run_id) 'Release Candidate - Verified Docker'
    Confirm-Run ([long]$dev.deployment_run_id) 'Deploy DEV - Verified GHCR Digest'
    if ($dev.image -eq $prod.image) { throw 'PROD already references DEV image.' }
    if ($dev.image -cnotmatch '^ghcr\.io/emadeq/advanced-regression-mlops@sha256:[a-f0-9]{64}$') {
        throw 'Invalid DEV image.'
    }
    $digestShort = (($prod.image -split ':')[-1]).Substring(0, 12)
    $date = (Get-Date).ToUniversalTime().ToString('yyyyMMdd')
    $archiveRelative = "releases/history/prod-$date-before-final-$digestShort.json"
    $archive = Join-Path (Get-Location).Path ($archiveRelative.Replace('/', '\'))
    if (Test-Path $archive) { throw "Archive already exists: $archiveRelative" }
    $new = [ordered]@{
        environment = 'prod'
        image = $dev.image
        release_run_id = [long]$dev.release_run_id
        dev_deployment_run_id = [long]$dev.deployment_run_id
        prod_deployment_run_id = $DeployRunId
        model_version = $dev.model_version
        api_url = $prod.api_url
        recorded_at_utc = $timestamp
    }
    & git switch -c $branch
    if ($LASTEXITCODE -ne 0) { throw 'Could not create branch.' }
    Copy-Item $prodPath $archive
    [System.IO.File]::WriteAllText($prodPath, (($new | ConvertTo-Json -Depth 10) + "`n"), $utf8)
    Write-Host "Archived prior PROD manifest: $archiveRelative" -ForegroundColor Cyan
    # Version-control durable release evidence even after 7-day CI artifacts expire.
    $evidence = @(
        '# Final MLOps demonstration - release evidence',
        '',
        "Recorded at (UTC): $timestamp",
        "Immutable GHCR image: $($dev.image)",
        "Source release workflow: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/$($dev.release_run_id)",
        "DEV verification: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/$($dev.deployment_run_id)",
        "PROD promotion: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/$DeployRunId",
        'Previously demonstrated guarded PROD rollback: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/39933134876',
        '',
        'The final release workflow checks DVC integrity, training quality, MLflow provenance,',
        'the model hash, training/serving dependency parity, security response headers and JSON logging.',
        'The DEV and PROD workflows check the exact image digest and all three live API endpoints.',
        'The source of truth is releases/dev.json and releases/prod.json.',
        'Render log inspection and free-service suspension are manual operational steps.',
        'Full temporary MLflow database and candidate model artifacts expire after seven days.'
    ) -join "`n"
    $evidencePath = Join-Path (Get-Location).Path 'docs\final-release-evidence.md'
    if (Test-Path $evidencePath) { throw 'Final release evidence already exists; do not overwrite.' }
    [System.IO.File]::WriteAllText($evidencePath, ($evidence + "`n"), $utf8)
}

Write-Host "Verified manifest prepared on branch $branch" -ForegroundColor Green
Write-Host "Image: $($new.image)"
& git status --short
if ($Environment -eq 'dev') { Write-Host 'Next: git add releases/dev.json' -ForegroundColor Yellow }
else { Write-Host 'Next: git add releases docs/final-release-evidence.md' -ForegroundColor Yellow }
Write-Host "Then: git commit -m 'docs: record verified final $Environment release'" -ForegroundColor Yellow
Write-Host "Then: git push -u origin $branch; gh pr create --fill; gh pr checks --watch; gh pr merge --squash --delete-branch"
