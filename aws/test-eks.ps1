param(
    [Parameter(Mandatory = $true)][string]$BaseUrl,
    [int]$TimeoutSeconds = 120
)
$ErrorActionPreference = 'Stop'
$BaseUrl = $BaseUrl.TrimEnd('/')
$health = Invoke-RestMethod "$BaseUrl/api/v1/health/" -TimeoutSec 15
if ($health.status -ne 'ok') { throw 'Health check failed' }
$docs = Invoke-WebRequest "$BaseUrl/docs" -TimeoutSec 15
if ($docs.StatusCode -ne 200) { throw 'Swagger is unavailable' }
$message = "EKS smoke test $([guid]::NewGuid())"
$job = Invoke-RestMethod "$BaseUrl/api/v1/messages/jobs" -Method Post -ContentType 'application/json' -Body (@{message=$message; email='eks-test@example.com'} | ConvertTo-Json) -TimeoutSec 15
$messageId = $job.'Message ID'
if (-not $messageId) { throw 'POST returned no Message ID' }
$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
do {
    $result = Invoke-RestMethod "$BaseUrl/api/v1/messages/$messageId/score" -TimeoutSec 15
    if ($null -ne $result.score) {
        if ($result.message -ne $message) { throw 'Returned score belongs to a different message' }
        if ([double]$result.score -lt 0 -or [double]$result.score -gt 1) { throw 'Score outside expected range' }
        Write-Output "PASS: Swagger, API, PostgreSQL, Kafka and worker. Message ID=$messageId; score=$($result.score)"
        exit 0
    }
    Start-Sleep -Seconds 3
} while ((Get-Date) -lt $deadline)
throw "No score received for message $messageId within $TimeoutSeconds seconds"
