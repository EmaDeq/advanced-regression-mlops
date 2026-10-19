$ErrorActionPreference = 'Stop'
$endpoint = 'http://127.0.0.1:8000'
Write-Host 'GET /health'
Invoke-RestMethod -Method Get -Uri "$endpoint/health" | ConvertTo-Json
$payload = @{
    CRIM = 0.00632; ZN = 18.0; INDUS = 2.31; CHAS = 0
    NOX = 0.538; RM = 6.575; AGE = 65.2; DIS = 4.09
    RAD = 1.0; TAX = 296.0; PTRATIO = 15.3; LSTAT = 4.98
} | ConvertTo-Json
Write-Host 'POST /predict (value is in thousands of historical USD)'
Invoke-RestMethod -Method Post -Uri "$endpoint/predict" -ContentType 'application/json' -Body $payload | ConvertTo-Json
