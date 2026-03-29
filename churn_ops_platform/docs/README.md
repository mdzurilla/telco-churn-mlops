# Churn Ops Platform Docs

This folder contains the working documentation for the portfolio MLOps-style churn platform.

The intent of these docs is to explain the key principles the project demonstrates:

- how a churn model can be served and monitored
- how retraining and promotion can be handled in a lightweight but structured way
- how audit traceability and historical replay can be preserved
- where the project intentionally stops short of pretending to be production-ready

## Documents

- `architecture.md`
  System design document covering components, request flows, storage layout, key decisions, and scaling path.

- `operating_model.md`
  Business and operational framing for how the churn model is used, what decisions it supports, acceptable failure, retraining cadence, and promotion ownership.

- `model_card.md`
  Current serving model summary covering intended use, features, metrics, thresholding, limitations, monitoring, and cautions.

- `runbooks.md`
  Lightweight operational procedures for scoring, batch jobs, historical replay, audit traceability, retraining review, and promotion review.

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
