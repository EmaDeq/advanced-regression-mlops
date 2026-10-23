# Lightweight API monitoring (no paid external service)

The FastAPI app writes **one JSON event to stdout** per HTTP request, with:
`event`, randomly generated `request_id`, `environment`, `method`, fixed `route`
(`/health`, `/model-info`, `/predict`, or `other`), `status_code`, and `latency_ms`.
Responses also include `X-Request-ID` for correlation with these custom logs.

The custom JSON event deliberately excludes input feature values, predictions,
request/response bodies, raw URLs, query strings and source IP addresses.
Other logs (for example, Uvicorn access logs or provider logs) follow their own
configuration and may contain additional metadata: avoid transmitting secrets.

**To inspect logs:** in Render, open the existing DEV or PROD service and choose
Logs. Filter for `http_request`, HTTP 5xx statuses, or unexpected latency. These
are application logs, not a permanent audit store or guaranteed-duration history.
There is no new endpoint exposing metrics publicly and no long-running telemetry
server, external database, or monitoring account.

**Manual checks (only when the service is already resumed):**

```powershell
$dev = 'https://advanced-regression-mlops-dev.onrender.com'
Invoke-RestMethod "$dev/health" -TimeoutSec 180
Invoke-RestMethod "$dev/model-info" -TimeoutSec 180
```

Use the corresponding PROD URL for production. Do not schedule hourly health
polling of Render Free services: regular requests can wake an idle service and
consume shared monthly free instance hours. Suspended services are intentionally
not monitored. Investigate persistent HTTP 5xx, model readiness failures, or
unexpectedly high latency using the existing Render Logs screen.

**Limitations:** in-memory request details are not stored across restarts, logs
may expire, and this setup offers no automated alerts, latency SLO, user
analytics, access control, or request rate limiting. Only approved images
should be deployed using the existing DEV/PROD promotion workflow. This
monitoring change alone does not deploy anything.
