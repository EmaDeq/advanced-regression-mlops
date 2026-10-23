# Release lineage: DVC data snapshot, model fingerprint, and CI MLflow

New manually dispatched release candidates use one training execution on a GitHub runner.
Before Docker packaging, `advanced_regression_mlops.release_provenance`:

1. Checks the downloaded `data/raw/boston.csv` bytes and size against the committed
   DVC pointer `data/raw/boston.csv.dvc`. A mismatch **fails the release**. The
   original DVC remote remains on the local Windows drive, not accessible to CI.
2. Confirms the trained model bytes match `artifacts/model.sha256`.
3. Logs the already trained model's hyperparameters, holdout metrics, model artifact,
   source commit and data/model fingerprints to an ephemeral CI-local MLflow SQLite
   store (`mlflow-ci.db`); **it does not retrain**.
4. Writes `reports/release-provenance.json` with the MLflow run ID, metrics, data
   checksum, model SHA256 and Python/package versions.
5. Embeds the JSON record inside the published immutable Docker image at
   `/app/artifacts/release-provenance.json` and saves a 7-day GitHub Actions artifact.

A release is rejected if the freshly downloaded OpenML CSV differs from the existing
DVC snapshot. This is intentionally fail-closed: investigate data normalization,
source drift, or library versions; do **not** silently update the DVC pointer.

The DVC `artifacts/model.joblib.dvc` pointer refers to a separately trained local
model, not automatically to each CI-built model. Each CI image instead identifies
its bundled model by SHA256 in the embedded provenance JSON. The temporary CI
MLflow database is not a permanent shared tracking server; after artifact expiry,
the model/data fingerprints and MLflow run ID remain inside the GHCR image while
full interactive experiment history may not be recoverable. This is a portfolio
MLOps lineage improvement, not a durable enterprise model registry.

## Verify a newly built candidate

In GitHub Actions, run **Release Candidate - Verified Docker** manually (publication
is optional). Check the new **Record verifiable CI release lineage in MLflow** step.
Download the `regression-candidate-<commit>` artifact to inspect the JSON report,
model checksum, metrics, and MLflow database. Do not deploy if that job fails.

The release workflow still uses existing GitHub CI and GHCR; no new Render service,
paid account, remote database or API key is required.


## Final release: training-serving dependency parity

The release captures `artifacts/runtime-constraints.txt` from the **same runner**
that trained the model (`pip freeze --exclude-editable`). The Dockerfile uses the
constraints during `pip install .` and verifies `pip check`. Smoke tests compare
the dependency constraints and provenance JSON byte-for-byte between runner and
container, and require matching scikit-learn, pandas and numpy versions. The
model is trained **once**; no retraining occurs in Docker. This improves
repeatability without requiring a paid dependency registry or shared MLflow.
The image also records its originating Git commit as an OCI revision label.
