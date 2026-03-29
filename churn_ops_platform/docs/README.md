# Churn Ops Platform Docs

This folder contains the working documentation for the portfolio MLOps-style churn platform.

## Documents

- `platform_overview.md`
  High-level explanation of the API, data flow, storage, and model lifecycle.

- `model_governance.md`
  Guidance for retraining, challenger review, promotion decisions, and drift interpretation.

- `portfolio_notes.md`
  Explicit notes on what is intentionally simplified for a portfolio project versus what would change in production.

- `batch_scoring_progress.md`
  Historical progress log from earlier implementation work.

## Current API Surface

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
