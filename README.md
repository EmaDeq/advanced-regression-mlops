# Advanced Regression MLOps

[![CI](https://github.com/EmaDeq/advanced-regression-mlops/actions/workflows/ci.yml/badge.svg)](https://github.com/EmaDeq/advanced-regression-mlops/actions/workflows/ci.yml)

An educational, zero-*additional*-cost MLOps portfolio project: Python 3.12,
scikit-learn, FastAPI, GitHub Actions, immutable Docker images on GHCR, optional
Render Free DEV/PROD, local DVC and MLflow.

> **Ethics:** Boston Housing / OpenML 531 is a historically problematic, tiny
> benchmark. The racially constructed `B` feature is excluded. Other features
> may still be proxies. **Never use the model for actual housing, financial,
> policy or other consequential decisions.** See [data ethics](docs/data_ethics.md).

## Verified milestones (23 October 2026)

- Tests, Ruff and PR checks protect `main`.
- A manually triggered candidate workflow trains a model **once**, verifies the
  DVC-tracked CSV checksum and model SHA-256, logs to a **temporary CI-local
  MLflow** store, records JSON provenance, and smoke-tests the Docker image.
- Publishing to GHCR is **opt-in** (`publish_image=true`). The published image
  is the same image that was smoke-tested, addressed by immutable SHA-256 digest.
- DEV uses an existing Render Free service; PROD promotion requires manual
  approval of the protected `prod` GitHub environment.
- A real PROD rollback from image B to image A succeeded (GitHub run
  `39933134876`). Both releases are preserved in `releases/history/`.
- The API now has privacy-conscious JSON request logs **in source code**. The
  currently deployed images predate that change, so the new logs are **not yet
  active on Render** until a new approved release is deployed.

### Git-tracked deployment state

| Environment | Recorded image | Notes |
| --- | --- | --- |
| DEV | B: `sha256:3a30a679c995966af9db43b90040a1c7d502295736ae5f433e3cd6110c558ea4` | Second tested image |
| PROD | A: `sha256:863eebb1e8100a4f1397ace09f53712301944904984205634d58850da9dd9a4f` | Restored by verified rollback |

The source of truth is `releases/dev.json` and `releases/prod.json`, **not** this
static table. Manifests record the approved image; they are not a live health
check. Render services may be suspended to conserve free hours.

## Local setup on Windows

Requirements: Git, Python 3.12, PowerShell and Internet for dependencies/OpenML.
Docker Desktop is optional for local image builds; Docker licensing depends on
how it is used.

```powershell
git clone https://github.com/EmaDeq/advanced-regression-mlops.git
cd advanced-regression-mlops
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1

.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

To run a local API using the locally trusted model, run
`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-api.ps1`
then open `http://127.0.0.1:8000/docs`. In a second terminal run
`powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke-test.ps1`.
`/health`, `/model-info`, and `/predict` serve an educational model with twelve
numeric features; the historical MEDV target is expressed in thousands of
historical USD.

## Manual release process (no automatic PROD deployments)

1. CI gates each PR; merge into protected `main` after checks.
2. Manually trigger `.github/workflows/release-candidate.yml` with
   `publish_image=true` only when you intend to retain a published GHCR image.
   Use `false` for a full, **unpublished**, provenance-checking rehearsal.
3. After a successful published release, manually trigger `deploy-dev.yml` with
   that **release run ID** (digest artifact lasts 7 days). Verify the DEV job.
4. Update `releases/dev.json` to the verified image digest and the successful
   release and DEV deployment run IDs, via PR and CI.
5. Resume existing PROD if suspended. Trigger `promote-prod.yml` with
   `confirmation=PROMOTE`; manually approve the protected `prod` environment.
   The workflow deploys the **same DEV-tested digest** and smoke-tests PROD.
6. Archive the previous PROD manifest and update `releases/prod.json` with the
   successful promotion run ID via PR.
7. For rollback, use `.github/workflows/rollback-prod.yml` with an archived
   manifest and explicit `confirmation=ROLLBACK`; approve `prod`; inspect the
   checked digest and three live API checks; update the manifest afterward.

Full procedures and safety checks: [rollback runbook](docs/rollback.md).
No workflow here creates a new Render service or upgrades one to a paid plan.
The existing optional `render.yaml` is a **starter Blueprint**, not the source
of truth for current image-based deployments: do not reapply it to running
services. The old webhook-based `.github/workflows/deploy.yml` was removed.
`Dockerfile` and `docker-build.yml` remain legacy educational examples; the
verified release path uses **`Dockerfile.release`** exclusively.

## Model, data and experiment lineage

- OpenML dataset 531, 506 rows, 12 usable features, with `B` excluded.
- 80/20 holdout split, seeded CV tuning of HistGradientBoostingRegressor;
  DummyRegressor and Ridge baselines.
- Successfully verified unpublished lineage rehearsal: GitHub run
  `39937525166`, holdout R2 `0.8756`, MAE `2.1019`, RMSE `3.02`.
- DVC dataset snapshot is checked byte-for-byte during a release; CI downloads
  OpenML data and uses canonical CRLF line endings to match the local DVC pointer.
- MLflow run ID, Git SHA, dataset hash, model SHA-256, hyperparameters,
  metrics and package versions are stored in `reports/release-provenance.json`
  during the release and embedded in **new release images**. They are not present
  in older A/B images built before this improvement.
- CI MLflow SQLite database and full artifacts are retained **seven days**.
  No always-on MLflow tracking server is configured. The separate local DVC
  model pointer does not automatically refer to each CI-trained model.

More: [release lineage](docs/release-lineage.md) and
[architecture](docs/architecture.md).

## Monitoring, security and cost

The API source logs a JSON event with request ID, method, fixed route name,
HTTP status and latency, excluding request bodies, feature values and predictions.
No continuous synthetic checks are scheduled on Render Free. The API is an
**unauthenticated public demo**, with **no application rate limiter, automated
alerting or drift detection**. This is not a production security guarantee.

See [monitoring](docs/monitoring.md), [security](docs/security.md) and
[roadmap](docs/roadmap.md). Never commit secrets, local MLflow databases or
training data; public GitHub Actions and GHCR have their own applicable limits.
Keep Render on Free, check the dashboard for usage, and **Suspend** DEV/PROD
when not needed to avoid consuming instance-hours. Do not add a payment method
if avoiding charges is paramount.

## Final acceptance and operations

The last planned MLOps release adds stricter holdout/baseline quality gates,
version-consistent training/serving dependencies, and Docker smoke tests that
check provenance, API security headers and structured logging. The final
published image must still pass DEV, protected PROD and manifest-reconciliation
checks before MLOps closure is claimed. See the
[final release checklist](docs/final-release-checklist.md) and the
[manifest recorder](scripts/record-verified-release.ps1).

License: MIT for repository code only. Third-party components and data have
independent terms.
