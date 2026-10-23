# Final MLOps demonstration - release evidence

Recorded at (UTC): 2026-10-23T11:38:16.3303961Z
Immutable GHCR image: ghcr.io/emadeq/advanced-regression-mlops@sha256:6e6afbdf6d3b5059c5bcb0864b6a49debd5f09b2dd39ea5245aba47a45a6dd6c
Source release workflow: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/39944257313
DEV verification: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/39944759927
PROD promotion: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/39947187429
Previously demonstrated guarded PROD rollback: https://github.com/EmaDeq/advanced-regression-mlops/actions/runs/39933134876

The final release workflow checks DVC integrity, training quality, MLflow provenance,
the model hash, training/serving dependency parity, security response headers and JSON logging.
The DEV and PROD workflows check the exact image digest and all three live API endpoints.
The source of truth is releases/dev.json and releases/prod.json.
Render log inspection and free-service suspension are manual operational steps.
Full temporary MLflow database and candidate model artifacts expire after seven days.
