# Roadmap â€” verified state on 23 October 2026

## Completed and demonstrated

- [x] Windows/Python scaffold, local training and ethical dataset limitations
- [x] Holdout evaluation, tuned regression and baseline comparisons
- [x] FastAPI inference endpoints and offline tests
- [x] GitHub branch protection, pytest/Ruff CI and reviewed PR merges
- [x] Local MLflow experiment logging and DVC dataset/model snapshots
- [x] Immutable smoke-tested Docker release, opt-in GHCR publishing
- [x] Controlled existing Render Free DEV deployment by exact image digest
- [x] Protected PROD promotion with manual approval and exact-digest checks
- [x] Real PROD rollback B -> A (run 39933134876), verified and archived
- [x] CI DVC dataset fingerprint plus model hash, MLflow run and lineage JSON
- [x] End-to-end unpublished provenance rehearsal (run 39937525166)
- [x] Privacy-conscious structured HTTP logs in source (PR #19)

## Completion activities

- [ ] Merge basic input hardening and accurate documentation (this PR)
- [ ] Build/publish one new approved image that includes monitoring, provenance
      and input-hardening changes; test DEV; optionally promote PROD under
      protected manual review and update manifests afterwards
- [ ] Examine Render logs for JSON request events *after* the new image is live
- [ ] Review cost limits and suspend the existing Free services when idle

## Optional further work (not required for MLOps portfolio v1)

- [ ] Authenticate public `/predict` or add a robust abuse/rate-limit solution
      if the application ever processes genuine user data
- [ ] Dependency/security scanning with reviewed update PRs
- [ ] Monitoring alerts and model drift/performance checks using appropriate
      labeled real-world inputs (not necessary for historical toy dataset)
- [ ] Explainability, alternative datasets/models, persistent model registry
- [ ] Separate React dashboard **after** MLOps operational closure

A hosted MLflow server, 24/7 uptime probes and paid external monitoring are
**not** prerequisites. CI MLflow SQLite and full artifacts are kept for seven
days; preserve important run artifacts offline if long-term comparisons matter.
