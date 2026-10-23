# PROD rollback runbook (educational Render Free deployment)

## Actually tested on 23 October 2026

- Approved original image A was promoted with PROD run `39771335358`.
- Different image B was promoted with PROD run `39921648054`.
- Real B -> A rollback **succeeded** with protected workflow run
  **`39933134876`**, including prior-run verification, live Render digest
  checks, and `/health`, `/model-info`, `/predict` smoke tests.
- Original A and superseded B manifests are archived in
  `releases/history/prod-20261022-initial.json` and
  `releases/history/prod-20261023-second.json` respectively.
- The current Git-tracked `releases/prod.json` records A and the successful
  rollback run ID; `releases/dev.json` still records B.

## Normal controlled release

1. Merge code to protected `main` with successful CI.
2. Manually run `release-candidate.yml` with `publish_image=true`. Verify
   DVC dataset and model checksums, MLflow provenance, tested Docker image
   and GHCR SHA-256 reference.
3. Resume existing DEV if suspended. Manually run `deploy-dev.yml`, passing
   the successful published release run ID. The digest artifact expires after
   seven days; retain its immutable digest in `releases/dev.json` through a PR.
4. Check DEV success, the reported exact live image and three API smoke tests.
5. Update `releases/dev.json` via PR with image and verified run IDs.
6. Resume existing PROD if suspended. Run `promote-prod.yml` with
   `confirmation=PROMOTE` and **manually approve** the protected `prod`
   environment. The workflow verifies DEV/release runs, deploys exactly the
   approved digest and smoke-tests PROD.
7. Archive superseded `releases/prod.json` under `releases/history/` and
   commit the new PROD image and workflow run ID via PR. Do not skip this.

## Roll back to an older approved image

1. Confirm older, DIFFERENT approved PROD image has an archived manifest and
   still exists on public GHCR. The current `releases/prod.json` must match
   the actual live Render deployment. If not, stop and reconcile first.
2. Trigger `rollback-prod.yml` on `main` with a path matching
   `releases/history/prod-*.json` and `confirmation=ROLLBACK`.
3. Manually approve the protected GitHub `prod` environment.
4. Workflow checks prior successful release/DEV/PROD runs, live image digest,
   redeploys the archived digest and smoke-tests the API. If any safeguard
   fails, **stop**: do not rerun blindly or change Git to conceal drift.
5. After success archive the superseded PROD manifest, update
   `releases/prod.json` with the restored digest and **new rollback run ID**,
   then merge through PR/CI.

## Safety and costs

- Git manifests are deployment records, not substitutes for checking Render.
- Rollback always requires human authorization and does not bypass `prod`
  environment gates. PROD/DEV use existing Free services; no workflow creates
  a new Render service or upgrades a plan.
- Both services share workspace Free instance-hour limits; suspend when idle.
  No 24/7 availability is guaranteed. Do not add billing details if avoiding
  charges is paramount.
- Do not use legacy `Dockerfile`, `render.yaml` Blueprint rebuilds, or removed
  webhook deployment for image-digest promotion. Retain approved GHCR images
  and release records for as long as you need reliable rollback.
- Older A/B images predate the later MLflow CI lineage and structured logging
  changes. Updating code on GitHub does NOT update live services until a new
  tested image is explicitly deployed.
