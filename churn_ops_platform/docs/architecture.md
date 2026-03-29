# Architecture

## Purpose

This document explains how the Churn Ops Platform is structured, how data moves through it, and why the current design choices were made.

The goal is not to present a generic MLOps platform. The goal is to show a focused architecture for one operational churn scoring system with a clear model lifecycle.

## System Scope

The platform supports one stable business problem:

- binary churn prediction for telco customers

The platform currently exposes one public API contract:

- API version: `v1`

The platform is centered on one active model family:

- `churn_hist_gradient_boosting`

This keeps the serving contract simple while still allowing multiple artifacts to exist across lifecycle stages.

## Architectural Goals

The current architecture is optimized for:

- clear separation between serving, challenger, and archived artifacts
- reproducible scoring through artifact-bundled preprocessing
- local-first execution with minimal infrastructure
- traceability of predictions through audit logs
- support for both real-time and batch scoring
- a lightweight but realistic retraining and promotion workflow

It is intentionally not optimized yet for:

- distributed execution
- multi-tenant access
- horizontal scale
- strict security boundaries
- production-grade orchestration

## Portfolio Framing

This platform is intentionally a portfolio architecture, not a claim of production readiness.

The purpose of the project is to prove that the core operational workflow can be designed and implemented end to end:

- model serving
- batch scoring
- audit logging
- monitoring summaries
- retraining
- challenger promotion
- historical replay

In other words, this project is evidence that the workflow can be built and reasoned about coherently. It is not presented as a finished enterprise application.

That distinction matters. A portfolio project should demonstrate:

- sound architecture
- good separation of concerns
- practical lifecycle thinking
- clear tradeoff awareness

It does not need to simulate every production dependency just to look more complete.

## Why Local-First Is Intentional

The local-first design is a deliberate architectural choice, not an accidental limitation.

For this project, local execution makes several things better:

- the full system can be run and inspected by one reviewer
- artifacts and metadata remain easy to understand
- lifecycle transitions are visible on disk
- the architecture stays focused on the core ML operations problem

Adding infrastructure only for appearance would weaken the project rather than strengthen it. For example:

- containerization is useful for packaging and environment consistency, but running Docker only on a local machine does not fundamentally change the architecture
- CI is useful for team workflows and automated quality gates, but a minimal pipeline alone does not prove operational maturity
- cloud-managed services would add realism only if the project were trying to demonstrate actual deployment ownership

This project therefore favors architectural clarity over infrastructure theater.

## Authentication And Authorization Boundary

Authentication and authorization are intentionally not implemented in this project.

This is not because they are unimportant. It is because a local-first portfolio project should not pretend that a hard-coded username and password flow is a realistic modern access strategy.

In most real environments, access control would be delegated to an external identity layer such as:

- enterprise SSO
- OAuth or OIDC providers
- reverse proxy or API gateway policies
- platform-level role enforcement

Adding a simple in-app login here would create the appearance of completeness without demonstrating the kind of identity integration that a real system would use.

The more honest architectural position is:

- acknowledge that access control is required in production
- keep it out of this portfolio implementation
- document where that responsibility would sit in a real deployment

In a production version, the most likely design would be:

- authentication handled upstream by an identity provider or gateway
- authorization enforced at the API layer for actions such as retraining and promotion
- audit logs enriched with caller identity and role information

## High-Level Components

The platform has five main layers.

### 1. API Layer

Location:

- `app/api/v1/routers/`

Responsibilities:

- expose FastAPI endpoints
- validate incoming request shapes
- delegate business logic to services
- return typed responses

Main routes:

- scoring
- batch
- monitoring
- training
- models
- health

### 2. Service Layer

Location:

- `app/services/`

Responsibilities:

- implement scoring logic
- manage model artifact access
- handle retraining
- process batch jobs
- log audit events
- compute monitoring summaries
- coordinate model promotion

This is the main orchestration layer of the platform.

### 3. Persistence Layer

Locations:

- `app/models/`
- `app/repositories/`
- `app/core/database.py`

Responsibilities:

- store operational metadata in SQLite
- map tables through SQLAlchemy models
- persist model promotion history
- read and write metadata files

Current persisted entities:

- `batch_jobs`
- `inference_logs`
- model promotion history in JSON

### 4. Artifact Layer

Locations:

- `artifacts/serving/`
- `artifacts/challenger/`
- `artifacts/archive/`
- `artifacts/source/`

Responsibilities:

- hold the active serving artifact
- hold challenger artifacts created during retraining
- preserve previously serving artifacts for replay
- store source bundle inputs used for retraining and inference preparation

### 5. UI Layer

Locations:

- `streamlit_ui/simple/`
- `streamlit_ui/ops/`

Responsibilities:

- provide lightweight user interfaces over the API
- support manual scoring, batch operations, registry review, and retraining workflows

## Runtime View

```text
Client or Streamlit UI
        |
        v
 FastAPI routers
        |
        v
   Service layer
   |     |      |
   |     |      +--> Local filesystem artifacts
   |     +---------> SQLite metadata
   +---------------> Scoring / retraining utilities
```

## Main Request Flows

## Real-Time Scoring Flow

Endpoint:

- `POST /v1/score`

Flow:

1. Request is validated against the scoring schema.
2. `ScoringService` loads the active artifact through `ModelRegistryService`.
3. Feature engineering artifacts bundled with the model are applied to the payload.
4. Tree-ready inference features are aligned to the artifact reference columns.
5. The model produces a churn probability.
6. The artifact threshold is applied to create the binary prediction.
7. `AuditService` logs the scoring event in `inference_logs`.
8. The API returns probability, prediction, threshold, and model identity.

Why this matters:

- the same artifact contains the information needed to keep scoring reproducible
- inference is not dependent on notebook-time assumptions
- each prediction is traceable to a specific model artifact

## Historical Scoring Flow

Endpoint:

- `POST /v1/score/historical/{artifact_id}`

Flow:

1. Request is validated against the same scoring schema as standard scoring.
2. `ScoringService` loads one archived artifact by `artifact_id`.
3. The payload is transformed using that artifact's stored preprocessing metadata.
4. The archived model produces a score and prediction.
5. The result is logged with the archived `artifact_id`.

Design reason:

- historical replay is isolated from the default serving path
- standard production scoring remains simple
- audit questions can be answered using the exact archived artifact

## Batch Scoring Flow

Endpoints:

- `POST /v1/batch-score`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/download`

Flow:

1. A CSV file is uploaded.
2. The API writes the file to `data/batch/inputs/`.
3. `JobService` creates a `batch_jobs` record with `queued` status.
4. FastAPI background tasks start `BatchService.process_batch_job`.
5. The job is marked `running`.
6. The CSV is read row by row.
7. Each row is validated and scored independently.
8. Each row creates an audit log entry with row status.
9. The scored output is written to `data/batch/outputs/`.
10. The job is marked `completed` or `failed`.

Design reason:

- row-level processing avoids failing the whole batch due to one bad record
- the job table gives visibility into progress and outputs
- background tasks keep the API contract simple for a local-first system

Current limitation:

- FastAPI background tasks are suitable for a portfolio project, but not a full production job orchestration strategy

## Retraining Flow

Endpoint:

- `POST /v1/training/retrain`

Flow:

1. A labeled CSV is uploaded.
2. `TrainingService` validates that the target column exists.
3. The source model bundle and feature artifacts are loaded from `artifacts/source/`.
4. The uploaded data is split into training and evaluation sets.
5. The same feature engineering logic is applied as part of training preparation.
6. A challenger HistGradientBoosting model is fit.
7. Thresholds are evaluated on the challenger evaluation probabilities.
8. Challenger and current serving model are compared on the same evaluation split.
9. A challenger artifact is written under `artifacts/challenger/v1/...`.
10. Metadata is returned to the caller, including metrics and selected threshold.

Design reason:

- retraining stays aligned with the serving contract
- challengers can be created safely without changing live traffic
- comparison against serving makes promotion a governance decision, not just a training event

## Promotion Flow

Endpoint:

- `POST /v1/models/{model_name}/promote`

Flow:

1. The requested challenger artifact is located.
2. The current serving artifact is copied into `archive` if one exists.
3. The challenger artifact is copied into the serving location.
4. Active model values are persisted to `.env`.
5. Promotion history is appended to `metadata/model_promotions.json`.
6. The in-memory model cache is reset.

Design reason:

- serving stays represented by one simple path
- old serving artifacts remain replayable
- promotions are explicit operational events

## Monitoring Flow

Endpoint:

- `GET /v1/monitoring/summary`

Flow:

1. `MonitoringService` queries `inference_logs`.
2. It aggregates totals, average probability, prediction counts, status counts, request source mix, and recent daily volume.
3. The API returns a compact operational summary.

Design reason:

- inference logs become the single source for lightweight monitoring
- the monitoring layer is easy to understand and extend

Current limitation:

- this is summary monitoring, not full observability
- latency, alerting, and distribution drift detection are not yet implemented

## Data Model

### `inference_logs`

Purpose:

- record every scoring event relevant for audit and monitoring

Important fields:

- request source
- request payload
- prediction
- probability
- threshold
- API version
- model name
- model version
- artifact ID
- status
- error message
- job ID
- row index
- created timestamp

### `batch_jobs`

Purpose:

- track uploaded batch jobs through their lifecycle

Important fields:

- job ID
- status
- created, started, and completed timestamps
- input and output file paths
- rows total
- rows processed
- model name
- model version
- error message

## Artifact Design

The architecture depends heavily on self-contained inference artifacts.

Each inference artifact contains enough information to reproduce scoring behavior:

- model object
- API version
- model name
- model version
- artifact ID
- threshold
- reference columns
- categorical and numerical column definitions
- feature engineering artifacts

This is a strong design choice for this project because it reduces training-serving skew and keeps inference logic deterministic.

## Directory Strategy

```text
artifacts/
  source/
    model_bundles/
    feature_engineering/
  serving/
    v1/
      churn_hist_gradient_boosting/
        inference_artifact.joblib
        metadata.json
  challenger/
    v1/
      churn_hist_gradient_boosting/
        artifact_<timestamp>_<id>/
  archive/
    v1/
      churn_hist_gradient_boosting/
        artifact_<timestamp>_<id>/
```

Why this structure works well:

- the serving path is stable and easy to resolve
- challenger artifacts are isolated
- archive artifacts remain addressable by ID
- retraining inputs are separated from deployable inference artifacts

## Key Design Decisions

### Decision 1: One stable model contract

Why:

- simpler API
- easier artifact management
- easier comparison across retrained versions

Tradeoff:

- less flexible than a multi-model platform

### Decision 2: Local filesystem for artifacts

Why:

- easy to inspect
- easy to version mentally during development
- low infrastructure overhead

Tradeoff:

- no built-in durability, remote sharing, or concurrency controls

### Decision 3: SQLite for operational metadata

Why:

- lightweight
- sufficient for local-first development
- simple setup for job and audit records

Tradeoff:

- not a strong choice for heavy concurrent production usage

### Decision 4: FastAPI background tasks for batch jobs

Why:

- simple asynchronous behavior without adding Celery, Redis, or orchestration infrastructure

Tradeoff:

- not resilient enough for serious distributed batch processing

### Decision 5: Audit-first monitoring

Why:

- the same logs support both traceability and basic ops reporting

Tradeoff:

- monitoring depth is constrained by what is logged today

## Failure Modes And Current Handling

Current architecture handles several common failures:

- invalid scoring payloads through request validation
- missing archived artifacts through `404` behavior
- row-level batch validation failures without stopping the full batch
- batch job execution failure with persisted failed status

Known gaps:

- no retry queue for batch jobs
- no dead-letter handling
- no formal artifact integrity checks
- no structured alerting
- no authentication or authorization layer

## Scaling Path

If this platform were expanded beyond portfolio scope, the most natural evolution would be:

1. Replace SQLite with PostgreSQL.
2. Replace local artifact storage with object storage such as S3, GCS, or Azure Blob.
3. Replace FastAPI background tasks with a real job runner or workflow system.
4. Add metrics, traces, and alerting.
5. Add auth, role-based access, and promotion controls.
6. Add CI/CD, containerization, and migration tooling.

The current design is intentionally shaped so these upgrades can be introduced without rewriting the core scoring contract.

## What This Architecture Demonstrates

The project demonstrates:

- artifact-based inference reproducibility
- clean separation of serving and model lifecycle stages
- operational traceability through audit logs
- support for both online and offline scoring modes
- a practical retraining and promotion workflow

It does not claim to be a complete production platform. It is a deliberately scoped architecture that shows how a churn model can be treated as an operational system rather than only a notebook output.
