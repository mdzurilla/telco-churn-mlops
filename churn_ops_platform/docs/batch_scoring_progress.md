# 📊 Churn Ops Platform — Batch Scoring & API Progress

## 🚀 What We Built Today

Today we moved from a simple scoring API to a **mini MLOps platform foundation** with asynchronous batch processing and job tracking.

---

## ✅ Core Achievements

### 1. Real-Time Scoring API
- Implemented `POST /v1/score`
- Added:
  - Strict schema validation (`Literal`, `Field`)
  - Input normalization (case handling, trimming)
  - Cross-field validation (business rules)
- Ensured:
  - No more `500` errors for bad input
  - Clean `422` responses

---

### 2. Async Batch Scoring API
Implemented:

- `POST /v1/batch-score`
- `GET /v1/jobs/{job_id}`
- `GET /v1/jobs/{job_id}/download`

#### Features:
- CSV upload support
- Background processing via FastAPI `BackgroundTasks`
- Job lifecycle tracking:
  - `queued → running → completed / failed`
- Output persisted as CSV

---

### 3. SQLite Job Tracking
- Introduced SQLAlchemy
- Created `batch_jobs` table
- Stored:
  - job metadata
  - status
  - timestamps
  - progress
  - file paths
- Enabled persistent job monitoring

---

### 4. Batch Processing Engine
- Built `BatchService`
- Implemented:
  - CSV ingestion
  - Row-by-row validation using `ScoreRequest`
  - Scoring via shared scoring service
  - Output generation

#### Key Design Choice:
✔️ **Row-level validation (not fail-fast)**

Each row:
- `success` → scored
- `validation_error` → captured
- `scoring_error` → captured

---

### 5. Output & Download
- Saved results to:
```
data/batch/outputs/
```

- Implemented download endpoint
- Added `download_url` to job status response

---

### 6. Clean Architecture Separation
Established clear layers:
```
API (schemas)
↓
Services (logic)
↓
Models (DB)
↓
Artifacts (ML)
```


---

## 🧠 What This Represents

We now have:

- Real-time inference API
- Async batch processing system
- Persistent job tracking
- Robust validation layer
- Reusable scoring logic
- Downloadable outputs

👉 This is effectively a **lightweight ML platform**

---

## 📈 What To Improve Next

### 1. 🔍 Inference Audit Logging (HIGH PRIORITY)

Add:
- `inference_logs` table

Track:
- input payload (or hashed/partial)
- prediction
- probability
- model version
- timestamp

#### Why:
- Enables monitoring
- Enables drift detection later
- Adds real production credibility

---

### 2. 📊 Monitoring Endpoint

Implement:
```
GET /v1/monitoring/summary
```

Metrics:
- prediction distribution
- average probability
- request volume
- basic trends

---

### 3. 📦 Batch Enhancements

- Add progress percentage:
```
rows_processed / rows_total
```

- Add job duration
- Add job listing endpoint:

```
rows_processed / rows_total
```

- Add job duration
- Add job listing endpoint:

```
GET /v1/jobs
```

---

### 4. 🧾 Error Handling Improvements

- Standardize error format
- Improve validation messages
- Add structured logging

---

### 5. 🧪 Testing

- Unit tests for:
- scoring service
- batch service
- Integration tests for API endpoints

---

### 6. 📊 (Future) Drift Detection

Given current constraints:
- simulate using test set
- compare:
- score distributions
- prediction rates

---

### 7. 🔁 (Future) Model Versioning & Promotion

Already planned endpoints:

- `GET /v1/models`
- `POST /v1/models/{model}/promote`

Next step:
- implement comparison logic
- store evaluation metrics

---

## ❌ What We Intentionally Skipped

- MLflow (not suitable for this setup)
- Full deployment (local-only scope)
- Real streaming data pipelines
- Complex retraining orchestration

---

## 🧠 Key Design Decisions

- Keep everything local (portfolio scope)
- Use SQLite instead of external DB
- Use BackgroundTasks instead of queue system
- Prioritize clarity over scalability

---

## 🏁 Current State

✔️ Functional API  
✔️ Async batch scoring  
✔️ Job tracking  
✔️ Output retrieval  
✔️ Validation layer  

👉 Ready for:
- monitoring
- audit logging
- platform narrative

---

## 💬 Summary

Today we transitioned from:

> “Serving a model”

to:

> **“Building a structured, extensible ML platform with real-time and batch capabilities.”**

---

## ▶️ Next Session Focus

**Implement:**
👉 Inference audit logging  
👉 Monitoring summary endpoint  

These will connect everything into a complete story:
- scoring
- tracking
- monitoring
- lifecycle

---