# Platform Overview

## Purpose

This project is a lightweight churn-scoring platform built around a single binary classification use case.

The goal is not to build a generic ML platform with many model families. The goal is to demonstrate the key principles of an end-to-end operational workflow for:

- real-time scoring
- batch scoring
- audit logging
- monitoring
- retraining
- challenger promotion
- historical replay of archived models

This is therefore a proof that the workflow can be built coherently, not a claim that the current implementation is production-ready.

## Core Design Choice

The platform serves one stable model contract:

- API version: `v1`
- model family: `churn_hist_gradient_boosting`

Multiple trained artifacts can exist under that same `v1` contract. This makes it possible to retrain and compare models without changing the public API.

## Main Functional Areas

### 1. Real-Time Scoring

Endpoint:

- `POST /v1/score`

Purpose:

- score one customer payload immediately
- validate request schema
- normalize input values
- return probability, prediction, threshold, and model identity

### 2. Historical Scoring

Endpoint:

- `POST /v1/score/historical/{artifact_id}`

Purpose:

- replay scoring using one archived artifact
- support audit and traceability
- answer questions like:
  "Which model produced a score three months ago?"

This endpoint is intentionally separate from standard scoring so the default production path remains simple.

### 3. Batch Scoring

Endpoints:

- `POST /v1/batch-score`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/download`

Purpose:

- upload a CSV
- process rows asynchronously
- keep job state in SQLite
- save scored output to disk

Batch scoring uses row-level validation. One bad row does not fail the whole batch.

### 4. Audit Logging

Audit logs record scoring events with:

- request source
- payload
- probability
- prediction
- threshold
- model name
- model version
- API version
- artifact ID
- timestamps

This is the minimum foundation required for monitoring and historical traceability.

### 5. Monitoring

Endpoint:

- `GET /v1/monitoring/summary`

Purpose:

- summarize inference activity from audit logs
- show request counts and trends
- show prediction distribution
- show source mix and status breakdown

### 6. Model Listing and Promotion

Endpoints:

- `GET /v1/models`
- `POST /v1/models/{model_name}/promote`

Purpose:

- expose currently known artifacts
- distinguish serving, challenger, and archive stages
- promote one challenger into serving
- preserve the old serving artifact in archive

### 7. Retraining

Endpoint:

- `POST /v1/training/retrain`

Purpose:

- accept a CSV upload
- retrain the HGB challenger model
- evaluate challenger and serving model on the same evaluation split
- save the challenger artifact
- return metrics and threshold selection result

## Artifact Layout

The artifact structure is organized by deployment stage and API version.

```text
artifacts/
  serving/
    v1/
      churn_hist_gradient_boosting/
        inference_artifact.joblib
        metadata.json

  challenger/
    v1/
      churn_hist_gradient_boosting/
        artifact_<timestamp>_<id>/
          inference_artifact.joblib
          metadata.json

  archive/
    v1/
      churn_hist_gradient_boosting/
        artifact_<timestamp>_<id>/
          inference_artifact.joblib
          metadata.json
```

## Lifecycle Summary

### Serving

The serving artifact is the currently active model used by `POST /v1/score`.

### Challenger

A challenger artifact is a retrained candidate that is not yet serving production traffic.

### Archive

An archived artifact is a previously serving model that was replaced by a later promotion.

Archived models remain available for historical scoring.

## Why This Structure Exists

The separation between `serving`, `challenger`, and `archive` solves three practical problems:

- production scoring stays simple
- challenger models can be created without affecting live scoring
- old production models remain callable for audit or replay

## Data and Storage

Current storage is local:

- SQLite for lightweight operational metadata
- local filesystem for batch input/output and model artifacts

This is intentional for a portfolio project. See `portfolio_notes.md` for the production tradeoffs.
