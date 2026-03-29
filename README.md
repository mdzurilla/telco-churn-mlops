# Binary Response Churn Modeling

![Python](https://img.shields.io/badge/Python-3.13-blue)

End-to-end churn modeling project built on the Telco Customer Churn dataset, extended with a production-style serving and MLOps layer in `churn_ops_platform`.

## What This Repository Includes

1. Modeling workflow (notebooks + reusable utilities):
- Data understanding, split, EDA, feature engineering, and pipeline preparation.
- Model training across multiple families (logistic regression, trees, boosting, SVM, neural nets).
- Threshold-aware evaluation and comparison on a common holdout set.

2. Operational platform (`churn_ops_platform`):
- FastAPI service for real-time and historical scoring.
- Async batch scoring with job tracking and downloadable outputs.
- Monitoring summary built from inference logs.
- Retraining to challenger artifacts and promotion to serving.
- Streamlit apps for simple scoring and operations workflows.

## Dataset

Telco Customer Churn Dataset: https://www.kaggle.com/datasets/blastchar/telco-customer-churn

- Customers: 7,043
- Features: 21
- Target: binary churn (`Churn`)
- Data ownership: I do not own this dataset; all credit belongs to the original dataset authors.

## Core Modeling Highlights

- Reproducible, artifact-driven feature engineering from JSON configs.
- Fair model comparison with aligned preprocessing.
- Decision calibration through threshold sweeps (not just default 0.5 cutoff).
- Final serving family centered on Histogram Gradient Boosting artifacts.
- Short modeling summary: see `model_docs.md`.

## Churn Ops Platform Highlights

Location: `churn_ops_platform/`

- API version: `v1`
- Active model family: `churn_hist_gradient_boosting`
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
- `artifacts/archive`: previously serving artifacts for replay/audit

## Repository Structure

```text
.
├── 01_data_overview.ipynb
├── ...
├── 08_model_evaluation_and_comparison.ipynb
├── src/
│   ├── model_data_loader/
│   └── utils/
├── data/
│   ├── raw/
│   ├── processed/
│   └── configs/
├── models/
└── churn_ops_platform/
    ├── app/
    ├── artifacts/
    ├── data/batch/
    ├── docs/
    ├── streamlit_ui/
    └── tests/
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

## Author

Matus Dzurilla

## License

Educational and portfolio use.
