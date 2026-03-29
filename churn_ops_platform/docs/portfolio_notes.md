# Portfolio Notes

## Scope

This project is intentionally designed as a portfolio-scale MLOps-style system, not a production-grade enterprise platform.

That means some choices are optimized for:

- clarity
- learnability
- end-to-end completeness
- reasonable local execution

rather than for large-scale production hardening.

## Intentional Simplifications

### Local File Storage

Artifacts, batch inputs, and batch outputs are stored on the local filesystem.

Why this is acceptable here:

- easy to inspect during development
- easy to demo
- keeps architecture understandable

What would change in production:

- object storage such as S3, Azure Blob Storage, or GCS
- managed retention rules
- stronger access controls
- checksum and integrity validation

### SQLite

Operational metadata is stored in SQLite.

Why this is acceptable here:

- minimal setup
- perfect for local demos
- enough for job tracking, audit logs, and lightweight monitoring

What would change in production:

- PostgreSQL or another managed relational database
- stronger concurrency support
- managed backups
- better migration tooling

### BackgroundTasks Instead of a Real Queue

Batch jobs use FastAPI background tasks.

Why this is acceptable here:

- simple
- readable
- enough to demonstrate asynchronous job handling

What would change in production:

- Celery, Dramatiq, Arq, Azure Functions, or another proper job orchestration mechanism
- retries
- dead-letter handling
- worker scaling

### Single Model Family

The platform only supports one model family:

- `churn_hist_gradient_boosting`

Why this is acceptable here:

- keeps the lifecycle focused
- avoids fake generality
- reflects a realistic first production deployment

What would change in production:

- maybe still a single family at first
- but stronger model registry and governance around candidate variants

### Manual Promotion Logic

Promotion is an explicit application action.

Why this is acceptable here:

- makes lifecycle behavior easy to explain
- avoids hidden automation
- keeps governance visible

What would change in production:

- approval workflows
- richer metadata tracking
- rollout checks
- stronger version-control around promotions

## What This Project Still Demonstrates Well

Even with those simplifications, the project still demonstrates important real-world ideas:

- API contract validation
- shared scoring logic
- asynchronous batch handling
- audit logging
- monitoring summaries
- challenger creation
- model promotion
- archival and historical replay

## Short Honest Summary

This project is local-first and intentionally lightweight.

In production, storage would move to blob/object storage, metadata would move to a stronger database, and orchestration would use more robust infrastructure.

But the architecture and lifecycle ideas shown here are still valid:

- separate serving and challenger states
- keep immutable archived artifacts
- log model identity during inference
- compare challenger and serving before promotion
- preserve the ability to replay historical scoring
