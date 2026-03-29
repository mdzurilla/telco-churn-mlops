# Churn Ops Platform

Churn Ops Platform is a portfolio-scale MLOps-style project for customer churn prediction.

It combines:

- real-time scoring
- asynchronous batch scoring
- inference audit logging
- monitoring summaries
- challenger retraining
- model promotion
- archived-model replay through historical scoring

The project is intentionally focused on one stable business use case and one model family:

- API contract: `v1`
- model family: `churn_hist_gradient_boosting`

Rather than pretending to support many pipelines, this project shows how a single churn model can be served, monitored, retrained, promoted, and audited in a structured way.

## Business Overview

The business problem is customer churn prediction.

The API is designed to support two kinds of work:

- operational scoring of individual customer records
- operational scoring of uploaded CSV datasets for campaigns, reviews, or backfills

The platform also supports model lifecycle tasks:

- retrain a challenger model from uploaded labeled data
- compare challenger vs serving performance
- promote a challenger into serving
- preserve the previous serving model in archive
- replay historical predictions with archived artifacts

## What The Project Demonstrates

- FastAPI-based inference API
- strict request validation and normalization
- batch job tracking with SQLite
- filesystem-based artifact lifecycle
- audit logging with model identity
- monitoring built from inference logs
- retraining and challenger creation
- historical scoring against archived artifacts

## Local-First By Design

This is a local-first portfolio project.

That means:

- SQLite is used for lightweight metadata
- model artifacts are stored on the local filesystem
- batch jobs use FastAPI background tasks

In production, these would likely become:

- PostgreSQL or another managed database
- S3 / Azure Blob / GCS for artifact storage
- a real job queue or orchestration layer

Those tradeoffs are documented in [portfolio_notes.md](c:/Users/matus/Repos/datascience/binary-response-churn-modeling/churn_ops_platform/docs/portfolio_notes.md).

## Project Structure

```text
app/
  api/
  core/
  models/
  repositories/
  services/
  utils/

artifacts/
  serving/
  challenger/
  archive/
  source/

data/
  batch/

docs/
tests/
```

## Run Locally

### 1. Create and activate a virtual environment

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run the API

```powershell
uvicorn app.main:app --reload
```

If you prefer to use the venv executable explicitly:

```powershell
.\.venv\Scripts\uvicorn.exe app.main:app --reload
```

### 4. Open the API docs

Once the server is running:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Basic Endpoints

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

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

## Documentation

More detailed documentation is available in [docs/README.md](c:/Users/matus/Repos/datascience/binary-response-churn-modeling/churn_ops_platform/docs/README.md).

Recommended reading order:

1. [platform_overview.md](c:/Users/matus/Repos/datascience/binary-response-churn-modeling/churn_ops_platform/docs/platform_overview.md)
2. [model_governance.md](c:/Users/matus/Repos/datascience/binary-response-churn-modeling/churn_ops_platform/docs/model_governance.md)
3. [portfolio_notes.md](c:/Users/matus/Repos/datascience/binary-response-churn-modeling/churn_ops_platform/docs/portfolio_notes.md)

## Current Lifecycle Summary

### Standard scoring

`POST /v1/score` uses the current serving artifact.

### Retraining

`POST /v1/training/retrain` creates a challenger artifact under `artifacts/challenger/v1/...`

### Promotion

`POST /v1/models/{model_name}/promote` promotes one challenger artifact into serving and moves the previous serving artifact into archive.

### Historical replay

`POST /v1/score/historical/{artifact_id}` scores a payload with one archived artifact.

## Why This Repo Exists

The purpose of this repository is to show that a churn model can be treated as an operational product, not just a notebook output.

That means the project focuses not only on model performance, but also on:

- input contracts
- scoring reliability
- traceability
- model lifecycle decisions
- reproducibility of past predictions
