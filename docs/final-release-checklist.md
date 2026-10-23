# Final MLOps release acceptance (educational demonstration)

This is the archived release acceptance procedure, not a claim of commercial
production readiness. **All release acceptance steps below were completed** on
23 October 2026 with final image C. See [recorded evidence](final-release-evidence.md).
The procedure remains as a checklist for future explicitly approved changes.

## Source acceptance

- Merge the final PR after required GitHub CI is green.
- Run `release-candidate.yml` once from protected `main` with
  `publish_image=true` (do not publish while investigating failures).
- The release fails if the OpenML snapshot bytes do not match the DVC pointer,
  test metrics fail quality gates, or the checksum does not match the model.
- Store dependency constraints from the *training runner*. Docker installs
  serving dependencies with these same exact versions. The smoke test verifies
  model/provenance files, package parity, request logging and security headers.
- The immutable published GHCR digest and successful release run ID identify
  the candidate. The full MLflow SQLite/artifacts last **seven days**; archive
  those important files offline when long-term experiment review matters.
  No shared MLflow model registry is deployed.

## DEV, then PROD (manual, guarded)

1. Resume the existing Render Free DEV service if suspended.
2. Run `deploy-dev.yml` on `main`, supplying the **published release run ID**.
   Require a successful SHA-256 digest check and all three API smoke tests.
3. Run `scripts/record-verified-release.ps1 -Environment dev
   -DeployRunId <DEV_RUN> -ReleaseRunId <RELEASE_RUN>` in PowerShell. Create a
   reviewed PR from its generated branch and merge after CI passes.
4. Manually inspect the DEV Render Logs for JSON `http_request` events.
   Observe `X-Request-ID`, `X-Content-Type-Options` and `Cache-Control` headers.
5. Resume the existing Free PROD service, if suspended. Run `promote-prod.yml`
   on `main` with `confirmation=PROMOTE` and manually approve environment `prod`.
   Require successful digest verification and all three API smoke tests.
6. Run `scripts/record-verified-release.ps1 -Environment prod
   -DeployRunId <PROD_RUN>` in PowerShell. It archives the prior PROD manifest,
   prepares the new record and prints the branch. Merge its PR after CI passes.
7. Confirm `releases/dev.json` and `releases/prod.json` contain the same new
   immutable digest and the correct successful run IDs. Record final run IDs
   in a release summary or GitHub Release if long-term documentation is desired.
8. Run `scripts/verify-final-release.ps1` on `main` after both manifest PRs
   merge. It verifies release/deploy run IDs, both endpoints, security headers
   and matching immutable digests. Check Render JSON logs separately.
9. Suspend DEV and PROD on Render when not in use. Never upgrade or recreate
   services merely to finish this educational exercise.

## Explicit limitations, not blockers

- Free Render services sleep/suspend; no uptime guarantee. Monitoring here
  is on-demand JSON logs, **not** continuous synthetic polling or alerts.
- The public educational API has no authentication or distributed rate
  limiting. Use no personal data, no consequential predictions, and suspend
  the demo when unattended to reduce possible abuse/free-hour consumption.
- Historical Boston Housing is tiny and ethically problematic; model metrics
  are a software quality gate, not a fairness/generalization guarantee.
- Python package versions are constrained within the release build, but
  OpenML/network access, Python base images and upstream packages are external
  dependencies: this is not a fully offline, hermetic reproducible build.
- Long-lived MLflow infrastructure, Kubernetes, a React dashboard, auto-
  retraining and data-drift monitoring are outside this portfolio v1.
- The previous rollback B -> A has been genuinely demonstrated in GitHub run
  `39933134876`. We do **not** need to repeat it to accept the final image.

**Final declaration:** the MLOps track is closed only after the final image
was actually verified in DEV and PROD, both manifests are synchronized, and
GitHub CI is green. Source merge alone is insufficient.
