# PROD rollback runbook (educational environment)

## What is currently verified

The initial PROD release is recorded in `releases/prod.json` and archived as
`releases/history/prod-20261022-initial.json`. The initial promotion workflow has
passed with the immutable GHCR image digest in that file.

**Important:** until a second, different approved image has been promoted into
PROD, this project has **not** demonstrated a genuine rollback. The rollback
workflow intentionally refuses to deploy an image already recorded as current.

## For a new approved PROD release

1. Build a new candidate in GitHub Actions, publish its exact smoke-tested GHCR image.
2. Deploy that digest to DEV, verify `/health`, `/model-info`, and `/predict`.
3. Update `releases/dev.json` via a reviewed PR to point to the verified new digest
   and successful release/DEV run IDs.
4. Use the protected `promote-prod.yml` workflow and manually approve `prod`.
5. Archive the prior `releases/prod.json` in `releases/history/`, then update
   `releases/prod.json` via PR with the new digest and successful PROD run ID.

## To roll back an unsuccessful new release

1. Confirm a **different**, older, approved PROD image exists in
   `releases/history/` and remains available publicly in GHCR.
2. Confirm `releases/prod.json` describes the image currently live on Render.
3. Manually run `Rollback PROD - Approved Image` from `main`, providing the
   archived manifest path and the explicit confirmation `ROLLBACK`.
4. Approve the protected `prod` environment in GitHub Actions. This is a
   deliberate operation, not an automatic background deployment.
5. The workflow validates the historic release/DEV/PROD GitHub runs, compares
   the live Render digest against `releases/prod.json`, deploys the older digest,
   waits for Render to report it live, and runs three live API smoke tests.
6. After a successful rollback, archive the superseded `releases/prod.json` and
   update `releases/prod.json` to record the restored digest and successful
   rollback run ID. Without this, the release manifest will be stale.

## Safety and cost

No workflow creates or upgrades a Render service. Keep the service set to Free;
DEV and PROD share the workspace's free instance-hours budget. This is an
educational environment, not an always-on commercially supported PROD system.

The archive is a historical record, **not** automatic proof of live state.
The workflow refuses to change PROD if the most recent live Render image differs
from the Git-tracked current PROD image. Using digest-based redeployment avoids
relying on Render's limited historic build retention, but the GHCR image must
remain available.

Retire the obsolete `deploy.yml` deployment-hook workflow, which could bypass
this controlled digest promotion. Do not manually deploy a Git-based rebuild to
PROD.
