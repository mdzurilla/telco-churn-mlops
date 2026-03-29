# Runbooks

## Purpose

This document describes how to operate the portfolio churn platform in practice.

These runbooks are intentionally lightweight. The goal is not to imitate a full production operations stack with tools such as MLflow, Airflow, or enterprise workflow systems. The goal is to show how this platform is meant to be used, checked, and explained when serving, batch processing, retraining, and audit traceability matter.

## Platform Scope

The platform supports four operational paths that matter most in day-to-day use:

- real-time scoring
- batch scoring
- historical scoring
- batch result retrieval and audit traceability

These are the core workflows because they cover both immediate operational use and later audit or reproducibility questions.

## Shared Operating Principle

For this project, traceability matters almost as much as scoring itself.

The reason is simple:

- if someone later claims that the model predicted something on a given record or file
- and that prediction mattered operationally or financially
- the platform should make it possible to trace how that result was produced

That is why the system logs model identity, artifact identity, thresholds, payloads, job IDs, and timestamps. The goal is to support reproducibility even much later, including audit-style review scenarios.

## Runbook 1: Real-Time Scoring

Use when:

- a single customer record needs to be scored immediately
- another internal system wants synchronous scoring
- an operator wants to inspect one case quickly

Endpoint:

- `POST /v1/score`

Normal flow:

1. Submit one payload to the scoring endpoint.
2. The platform validates the request against the scoring schema.
3. The active serving artifact is loaded.
4. The stored preprocessing artifacts are applied.
5. The model returns probability, prediction, threshold, and model identity.
6. The event is written to the audit log as a `realtime` request.

What to check when results look wrong:

- confirm the payload matches the expected schema
- confirm the active serving model is the intended artifact
- confirm the returned threshold and artifact ID are the expected ones
- confirm the input values reflect the customer state you intended to score

Expected output:

- one score response
- one audit trail entry

## Runbook 2: Batch Scoring

Use when:

- a team wants to score many customers at once
- a campaign list or review list needs churn probabilities
- an offline operational dataset needs to be processed

Endpoints:

- `POST /v1/batch-score`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/download`

Normal flow:

1. Upload a CSV file to `POST /v1/batch-score`.
2. Capture the returned `job_id`.
3. Poll `GET /v1/jobs/{job_id}` until the job is completed or failed.
4. If completed, download results from `GET /v1/jobs/{job_id}/download`.

Important operating behavior:

- the job is asynchronous
- rows are validated individually
- one bad row does not fail the whole batch
- each row can generate its own audit entry

What to check during execution:

- job status
- rows processed versus rows total
- model name and version recorded on the job
- whether output file path was created

Expected output:

- a scored CSV with row-level result columns
- job metadata in SQLite
- row-level inference logs for audit

## Runbook 3: Historical Scoring

Use when:

- someone asks which artifact produced a past result
- a prior score needs to be replayed against an archived model
- audit or model traceability requires exact historical reproduction

Endpoint:

- `POST /v1/score/historical/{artifact_id}`

Normal flow:

1. Identify the archived `artifact_id` that should be replayed.
2. Send the payload to `POST /v1/score/historical/{artifact_id}`.
3. The platform loads that archived artifact instead of the current serving artifact.
4. The payload is scored using the preprocessing and threshold stored inside that archived artifact.
5. The replay result is logged as a `historical` scoring event.

Why this exists:

- the active serving model may no longer match the model that produced an older result
- archived artifacts preserve exact replay capability
- audit responses need artifact-level reproducibility, not memory or guesswork

Expected output:

- score response using the requested archived artifact
- audit entry tied to that artifact

## Runbook 4: Batch Result Retrieval And Audit Trace

Use when:

- a past batch needs to be reviewed again
- an internal team questions a previous scored file
- an auditor asks how a prior batch output was produced

Normal flow:

1. Identify the batch `job_id`.
2. Review job metadata through `GET /v1/jobs/{job_id}`.
3. Retrieve the batch output file if it still exists.
4. Use the job ID and row index in `inference_logs` to trace row-level outcomes.
5. If needed, inspect the artifact ID stored in the log to determine whether the score came from serving or historical replay.

What should be recoverable:

- when the job ran
- which model and version were used
- which rows succeeded
- which rows had validation or scoring errors
- what output file was produced

Why this matters:

- reproducibility is not only about single predictions
- batch outputs often drive real campaign or customer-care actions
- later audit questions may focus on one specific row inside a much larger batch

## Failure Runbook: Real-Time Scoring Looks Suspicious

Symptoms:

- probability seems implausible
- prediction differs from expectation
- downstream team reports a surprising score

Checks:

1. Confirm the exact request payload.
2. Confirm whether scoring used the live endpoint or historical replay.
3. Confirm the returned `artifact_id`, `model_name`, `model_version`, and `threshold`.
4. Verify that the input fields reflect the intended customer state.
5. If needed, replay the same payload through historical scoring if the question concerns an archived artifact.

Likely causes:

- payload mismatch
- misunderstanding of current serving artifact
- real model behavior shift
- business expectation mismatch rather than system failure

## Failure Runbook: Batch Job Failed

Symptoms:

- job status is `failed`
- no download URL is available
- output file does not exist

Checks:

1. Inspect `GET /v1/jobs/{job_id}`.
2. Review `error_message` on the job record.
3. Confirm the uploaded file was a valid CSV.
4. Check whether the input file path exists.
5. Review whether the failure happened before row-level processing or during it.

Likely causes:

- invalid file structure
- unexpected runtime failure during processing
- data shape incompatible with the expected scoring schema

Operational note:

- row-level validation errors should not fail the entire batch
- a full job failure usually indicates a broader file or runtime issue

## Failure Runbook: Historical Replay Cannot Be Performed

Symptoms:

- archived artifact is not found
- `POST /v1/score/historical/{artifact_id}` returns `404`

Checks:

1. Confirm the exact `artifact_id`.
2. Confirm the artifact should exist in `artifacts/archive/v1/churn_hist_gradient_boosting/`.
3. Confirm the issue is really about replay of an archived model and not the active serving model.

Likely causes:

- wrong artifact ID
- replay requested for an artifact that was never archived
- missing archive content in the local environment

Operational note:

- this portfolio project assumes archived artifacts remain available locally
- in a real production environment, this would require stronger storage durability guarantees

## Failure Runbook: Reproducibility Question From Audit Or Control Review

Use when:

- someone states that a prior prediction or batch output must be justified
- a control function or external auditor wants the exact model path
- a historical prediction needs to be defended with evidence

Response pattern:

1. Identify whether the question concerns real-time scoring, batch scoring, or historical replay.
2. Retrieve the relevant audit log record or batch job.
3. Capture:
   - request source
   - request payload
   - prediction
   - probability
   - threshold
   - model name
   - model version
   - artifact ID
   - timestamp
4. If the artifact is archived, replay the same payload using `POST /v1/score/historical/{artifact_id}`.
5. Compare the reproduced result to the stored audit record.

What this runbook is meant to prove:

- the system is not only making predictions
- it preserves enough metadata to reconstruct how a result was produced

This is one of the most important operational stories in the project.

## Promotion Review Runbook

Use when:

- a challenger model has been trained
- a decision must be made on whether it should replace the current serving model

Checks:

1. Review challenger versus serving metrics on the same evaluation split.
2. Focus first on ranking quality:
   - `pr_auc`
   - `auc`
3. Then review thresholded behavior:
   - recall
   - precision
   - false positives
   - false negatives
4. Decide whether the challenger improves the business tradeoff, not only one metric.
5. Promote only if the result is understandable enough to explain to downstream users.

Operational note:

- promotion is an intentional business and model-governance decision
- it should not happen only because retraining produced a new artifact

## Retraining Review Runbook

Use when:

- fresh labeled data becomes available
- the team wants to check whether the current modeling approach still holds

Checks:

1. Retrain a challenger on fresh data.
2. Compare challenger and serving performance on the same evaluation split.
3. Check whether `pr_auc` and `auc` remain broadly stable.
4. Interpret changes in the context of acceptable tolerance, roughly `2%` to `5%`.
5. If retraining no longer restores acceptable ranking quality, escalate to deeper modeling review.

What escalation means in this project:

- revisit EDA
- revisit feature engineering
- revisit model family choice
- investigate whether business conditions changed materially

## What These Runbooks Demonstrate

These runbooks are intentionally simple, but they show the intended operating behavior of the platform:

- scoring should be easy to use
- batch processing should be traceable
- historical replay should support auditability
- retraining should be a controlled check, not an automatic replacement
- promotion should be explainable in business terms

This is the level of operational discipline the portfolio project is designed to demonstrate.
