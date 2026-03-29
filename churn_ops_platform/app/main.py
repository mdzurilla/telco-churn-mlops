from fastapi import FastAPI
from app.api.v1.routers import scoring, batch, training, models, monitoring, audit
from app.core.database import Base, engine
from app.models.batch_job import BatchJob  # noqa: F401
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Churn Ops Platform API")

Base.metadata.create_all(bind=engine)

app.include_router(scoring.router, prefix="/v1", tags=["Scoring"])
app.include_router(batch.router, prefix="/v1", tags=["Batch"])
# app.include_router(training.router, prefix="/v1", tags=["Training"])
# app.include_router(models.router, prefix="/v1", tags=["Models"])
# app.include_router(monitoring.router, prefix="/v1", tags=["Monitoring"])
# app.include_router(audit.router, prefix="/v1", tags=["Audit"])