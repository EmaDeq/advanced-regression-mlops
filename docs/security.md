# API security posture (educational public demo)

## Implemented safeguards

- Model inputs use a Pydantic schema with twelve canonical features; unknown
  keys are rejected. The historically problematic `B` predictor is excluded.
- Non-finite numeric values (NaN and positive/negative infinity) are rejected
  by `HousingFeatures` validation rather than passed to scikit-learn.
- The HTTP middleware adds `X-Content-Type-Options: nosniff` and
  `Cache-Control: no-store` to responses, plus a random `X-Request-ID`.
- Custom request logs capture **only** method, canonical route, status,
  elapsed milliseconds, environment and random ID. They exclude feature
  values, predictions, request bodies, query strings and raw URLs.
  Other Uvicorn/provider logs may include additional metadata, including IPs.
- `Dockerfile.release` verifies the model SHA-256, does not retrain, and runs
  the API under a non-root container user. Only trusted locally generated
  joblib/pickle models should ever be deserialized.
- CI enforces tests and Ruff; manually approved PROD promotion and rollback
  verify immutable Docker digests and live endpoints.

## Important limitations

- The endpoints `/health`, `/model-info`, `/predict` and interactive API docs
  are **public and unauthenticated**. There is no application rate limiting,
  WAF guarantee, durable audit log or automated intrusion detection.
- This public demo must use no personal data or secrets, and must not inform
  real-world housing decisions. Input validation does not provide full abuse
  resistance. An adversary could consume service resources or exhaust the
  Render Free allowance; suspend the services when not in use.
- Secret `RENDER_API_KEY` and variable `RENDER_SERVICE_ID` are configured in
  GitHub environments, not committed. Keep credentials private; rotate any
  leaked keys. Never put secrets in request bodies or query parameters.
- The final approved image C includes these safeguards and was verified in DEV
  and PROD. Historical A/B images remain archived as prior releases.
- Local and CI MLflow are not centralized durable audit systems. GitHub
  artifact retention is seven days for release candidates.

## Future option

If this ever becomes a real public-facing product, implement an authentication
plan and upstream/shared rate limiting with safe operational defaults, and
review logs, model ethics, provider quotas and secret management first. These
are intentionally outside the zero-cost educational v1 scope.
