# Advanced Regression MLOps

A **zero-additional-cost** personal-laptop MLOps portfolio starter for Boston Housing
regression. Cookiecutter Data Science-inspired structure; Python 3.12, scikit-learn,
FastAPI, pytest, Docker, GitHub Actions, and optional Render free-tier DEV/PROD services.

> **Ethics:** Boston Housing is a historically problematic dataset. The racially
> constructed `B` feature is deliberately **excluded** from model training and API input.
> Other variables can still act as proxies. This is an *educational benchmark only*,
> not a system for real-world housing decisions. See `docs/data_ethics.md`.

## Requirements (personal laptop)

- Windows PowerShell 5.1+; Windows 10/11.
- Python **3.12** recommended; Git; Internet for installing packages and fetching OpenML ID 531.
- Docker Desktop **optional** (free for personal use under Docker's license).
- GitHub CLI `gh` **optional** (for repository creation via the terminal).

No paid products are installed by this project. `setup.ps1` never signs up for a service
or initiates cloud deployment. Python packages download only from pip and the dataset
from OpenML. Always inspect scripts before running them.

## Quick start: Windows PowerShell

From the folder containing the downloaded ZIP:

```powershell
New-Item -ItemType Directory -Force -Path C:\mio | Out-Null
Expand-Archive -LiteralPath .\advanced-regression-mlops-starter.zip -DestinationPath C:\mio -Force
Set-Location C:\mio\advanced-regression-mlops
powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

`setup.ps1` creates `.venv`, installs project + test dependencies, runs tests, downloads
Boston from OpenML, trains an advanced tuned HistGradientBoostingRegressor, and creates
`artifacts/model.joblib`. It leaves a local Git repo on branch `main` if Git exists.
The OpenML fetch requires Internet **on first run**. To set up packages without training,
use `powershell -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -SkipTraining`.

### Run the API (first PowerShell terminal)

```powershell
.\scripts\start-api.ps1
```

Open `http://127.0.0.1:8000/docs` for interactive prediction requests. In a **second**
PowerShell terminal, in the project folder:

```powershell
.\scripts\smoke-test.ps1
```

Or manually:

```powershell
.\.venv\Scripts\python.exe -m advanced_regression_mlops.train --n-iter 8
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

If script execution is blocked, use `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-api.ps1` instead.

### GitHub setup (you control when to publish)

```powershell
git status
git add .
git commit -m "feat: bootstrap advanced regression MLOps"
# Install optional GitHub CLI: winget install --id GitHub.cli -e
# Log in interactively: gh auth login
# The following deliberately creates a PUBLIC repository for free public Actions:
gh repo create EmaDeq/advanced-regression-mlops --public --source . --remote origin --push
```

Change `--public` to `--private` if desired, but private GitHub Actions minutes have
account-specific quotas. Do **not** push secrets or local model/data artifacts.

### Local Docker (optional)

```powershell
docker build -t advanced-regression-mlops:local .
docker run --rm -p 8000:8000 advanced-regression-mlops:local
```

The starter Dockerfile downloads OpenML and **trains at build time**, so the image contains
its own model. This is convenient for a starter but **not yet production-grade artifact
promotion**. A future milestone will build one versioned model and promote an identical,
tested immutable image from DEV to PROD. No paid cloud resources are created.

### CI / CD and Render (optional; not enabled by default)

- `.github/workflows/ci.yml`: lint, formatting, and offline unit tests on push/PR.
- `.github/workflows/docker-build.yml`: manually trigger a full Docker image build.
- `render.yaml`: two explicitly **free-plan** services for `dev` and `prod`, with
  auto deploy **off**. Review the Render dashboard carefully **before** accepting a Blueprint.
- `.github/workflows/deploy.yml`: workflow manually triggered via **Actions → Deploy (opt-in)**.
  It runs tests, then POSTs the relevant Render deploy hook if configured. For each
  GitHub *environment* (`dev` / `prod`) create an environment secret named
  `RENDER_DEPLOY_HOOK_URL` copied from that service's Render Settings. Never commit hooks.
- Do **not** add a payment method to Render if zero financial risk is critical.
  Free services have limits, sleep when idle, and can be suspended. Two services share
  the workspace's free instance-hours budget. This is for learning, not reliable 24/7 hosting.
- Production-grade gating: set repository branch policies and manual approval rules where
  your GitHub plan supports them; restrict who can trigger production workflows.

**Warning:** The starter deploy hook tells Render to rebuild its connected Git branch.
It does not yet guarantee promotion of the exact image verified in DEV. That is on the
roadmap; don't use the current setup for consequential production systems.

## Model design

- OpenML dataset ID `531`, canonical 506-row Boston dataset; 12 input features (omit `B`).
- Train/test split **before** hyperparameter search (`random_state=42`).
- Mean-predicting DummyRegressor and scaled Ridge baselines.
- `Pipeline(SimpleImputer, HistGradientBoostingRegressor)`, RandomizedSearchCV, 5-fold CV.
- MAE, RMSE, R² on held-out test partition; metadata and artifacts saved locally.
- Housing target `MEDV` is **$1,000 USD units** from the historic dataset, not current values.
- Deterministic random seeds; small `--n-iter 6` during quick initial setup.

## Repository layout

```text
advanced-regression-mlops/
├── .github/workflows/     # CI, manual image build, opt-in CD
├── data/raw/              # downloaded once, never committed
├── artifacts/             # trained model, never committed
├── docs/                  # cloud deployment, ethics, architecture, roadmap
├── notebooks/             # optional exploratory notebooks
├── reports/               # generated metrics, figures
├── scripts/               # PowerShell commands and API smoke test
├── src/advanced_regression_mlops/
│   ├── api.py             # FastAPI endpoints
│   ├── data.py            # OpenML + schema verification
│   ├── modeling.py        # sklearn pipelines
│   └── train.py           # split, CV search, evaluation, serialization
├── tests/                 # fast offline unit and API tests
├── Dockerfile
├── render.yaml
├── pyproject.toml
└── setup.ps1
```

License: MIT **for code only**. Dataset and third-party package licenses are independent.

## CI Status
![CI](https://github.com/EmaDeq/advanced-regression-mlops/actions/workflows/ci.yml/badge.svg)
