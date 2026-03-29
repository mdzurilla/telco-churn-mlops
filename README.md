# Binary Response Churn Modeling

![Python](https://img.shields.io/badge/Python-3.13-blue)

End-to-end churn modeling project built on the Telco Customer Churn dataset, extended with an operational `churn_ops_platform` that demonstrates how a churn model can be served, monitored, retrained, promoted, and audited.

This repository is a portfolio project and a proof that the workflow can be designed and implemented end to end. It is not presented as a finished production application.

The focus is on:

- reproducible modeling
- artifact-driven inference
- decision-aware evaluation
- operational lifecycle design for one churn use case

The focus is not on pretending every production dependency already exists. Local-first choices such as filesystem artifacts, SQLite metadata, and FastAPI background tasks are intentional so the architecture stays inspectable and easy to run.

What this repository is trying to prove:

- churn modeling can be made reproducible
- model evaluation can be tied to business decisions, not just default metrics
- a lightweight MLOps-style lifecycle can be demonstrated without pretending to be a full production platform
- audit traceability and historical replay are first-class concerns, not afterthoughts

## What This Repository Includes

1. Modeling workflow:
- data understanding, split, EDA, feature engineering, and data preparation
- model training across multiple algorithm families
- threshold-aware evaluation and comparison on a common holdout set

2. Operational platform in `churn_ops_platform`:
- FastAPI service for real-time and historical scoring
- async batch scoring with job tracking and downloadable outputs
- monitoring summary built from inference logs
- retraining to challenger artifacts and promotion to serving
- Streamlit apps for simple scoring and operations workflows

## Portfolio Scope

This repo is meant to show that the core workflow can be built coherently:

- train and compare churn models
- preserve preprocessing and inference artifacts
- expose a stable scoring API
- support batch and real-time scoring
- log predictions for audit and monitoring
- retrain challenger models and promote them intentionally

It is not meant to claim:

- production-ready infrastructure
- enterprise authentication and authorization
- distributed job orchestration
- cloud deployment maturity

Those are valid next steps in a real environment, but not in this portfolio theoretical project.

## Dataset

Telco Customer Churn Dataset: https://www.kaggle.com/datasets/blastchar/telco-customer-churn

- Customers: 7,043
- Features: 21
- Target: binary churn (`Churn`)
- Data ownership: I do not own this dataset; all credit belongs to the original dataset authors.

## Core Modeling Highlights

- Reproducible, artifact-driven feature engineering from JSON configs
- Fair model comparison with aligned preprocessing
- Decision calibration through threshold sweeps, not only the default `0.5` cutoff
- Final serving family centered on Histogram Gradient Boosting artifacts
- Short modeling summary: `model_docs.md`

## Churn Ops Platform Highlights

Location: `churn_ops_platform/`

- API version: `v1`
- Active model family: `churn_hist_gradient_boosting`
- Architecture note: this is a local-first portfolio implementation that proves the lifecycle can be built; it is not marketed as a finished enterprise platform
- Main endpoints:
  - `GET /v1/health`
  - `POST /v1/score`
  - `POST /v1/score/historical/{artifact_id}`
  - `POST /v1/batch-score`
  - `GET /v1/jobs/{job_id}`
  - `GET /v1/jobs/{job_id}/download`
  - `GET /v1/monitoring/summary`
  - `GET /v1/models`
  - `POST /v1/models/{model_name}/promote`
  - `POST /v1/training/retrain`

Artifact lifecycle:
- `artifacts/serving`: active model
- `artifacts/challenger`: retrained candidates
- `artifacts/archive`: previously serving artifacts for replay and audit

## Repository Structure

```text
.
|-- 01_data_overview.ipynb
|-- ...
|-- 08_model_evaluation_and_comparison.ipynb
|-- src/
|   |-- model_data_loader/
|   `-- utils/
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- configs/
|-- models/
`-- churn_ops_platform/
    |-- app/
    |-- artifacts/
    |-- data/batch/
    |-- docs/
    |-- streamlit_ui/
    `-- tests/
```

## Quick Start

### A) Modeling Workflow

From repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then run notebooks from `01_...` to `08_...` as needed.

### B) Churn Ops Platform

```powershell
cd churn_ops_platform
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs:

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

Optional Streamlit UIs:

```powershell
streamlit run streamlit_ui/simple/app.py
streamlit run streamlit_ui/ops/app.py
```

## Tests

Platform tests:

```powershell
cd churn_ops_platform
python -m unittest discover -s tests -p "test_*.py" -v
```

## Documentation

- Modeling summary: `model_docs.md`
- Platform docs: `churn_ops_platform/docs/README.md`
- Architecture: `churn_ops_platform/docs/architecture.md`
- Operating model: `churn_ops_platform/docs/operating_model.md`
- Model card: `churn_ops_platform/docs/model_card.md`
- Runbooks: `churn_ops_platform/docs/runbooks.md`

## Author

Matus Dzurilla

## License

Educational and portfolio use.
