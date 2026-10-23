# Architecture â€” verified release flow (23 October 2026)

```text
LOCAL WINDOWS LAPTOP
  Python venv + local MLflow + DVC-managed CSV/model + local DVC storage
                |
                v
GITHUB (protected main, required CI on PR)
  Manual release-candidate.yml
    1. install/test (pytest, Ruff)
    2. fetch OpenML 531 -> canonical CSV -> check DVC pointer checksum
    3. train tuned model ONCE -> holdout quality gate -> SHA-256
    4. log that model/metrics to temporary MLflow SQLite
    5. provenance JSON (Git SHA, data/model hashes, MLflow ID, versions)
    6. Dockerfile.release packages model + provenance; no retraining
    7. smoke-test the Docker API
    8. optional publish exactly tested image to public GHCR by digest
                |
                v
  DEV: deploy-dev.yml -> existing Render Free DEV -> smoke tests
       update releases/dev.json through CI-checked PR
                |
                v
  PROD: promote-prod.yml -> protected environment manual approval
        -> existing Render Free PROD -> exact digest + smoke tests
        archive prior release, update releases/prod.json via PR
                |
                v
  ROLLBACK: rollback-prod.yml -> manual approval, archived approved
            manifest, live digest checks, redeploy older image, tests
            -> update releases/prod.json after success
```

### Verified and deliberately limited

- Historical original image A was restored after promotion of image B.
  Successful PROD rollback run: `39933134876`; both historical records live
  under `releases/history/`.
- CI provenance demo run `39937525166` completed successfully with
  `publish_image=false`. This was a **build-only** rehearsal, not a DEV or PROD
  deployment and not a persisted GHCR image.
- Source now contains privacy-conscious structured request logging (PR #19),
  but current A/B Render images do **not** contain those newer changes.
- The release MLflow SQLite backend and full candidate artifacts live on an
  ephemeral GitHub runner and in GitHub artifacts for seven days. The metadata
  embedded in newly published GHCR images can outlive that period, provided
  those images are retained. No shared tracking server or paid database.
- DVC stores the original dataset/model snapshot on the laptop; the build
  verifies dataset bytes against the committed pointer. The DVC model pointer
  is a different local training artifact, not the CI image's model identity.
  The latter is recorded using its SHA-256 hash in provenance JSON.
- Legacy `Dockerfile` trains during build; **do not use** it for verified
  image promotion. `Dockerfile.release` is canonical.
- `render.yaml` is optional bootstrap reference only. Existing services are
  image-based and manually managed; do not recreate them from this Blueprint.
- The demo has no centralized metrics dashboard, request rate limiting,
  authentication, synthetic uptime checks, drift alerts, or durable MLflow
  registry. It is not a commercial production system.

See [monitoring](monitoring.md), [security](security.md),
[release lineage](release-lineage.md), and [rollback](rollback.md).
