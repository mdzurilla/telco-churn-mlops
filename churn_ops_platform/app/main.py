from sqlalchemy import inspect, text
from fastapi import FastAPI
from app.api.v1.routers import scoring, batch, training, models, monitoring, audit, health
from app.core.database import Base, engine
from app.models.batch_job import BatchJob  # noqa: F401
from app.models.inference_log import InferenceLog  # noqa: F401
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="Churn Ops Platform API")

Base.metadata.create_all(bind=engine)


def ensure_inference_log_columns() -> None:
    inspector = inspect(engine)
    if "inference_logs" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("inference_logs")}
    statements: list[str] = []

    if "api_version" not in existing_columns:
        statements.append("ALTER TABLE inference_logs ADD COLUMN api_version VARCHAR(20) DEFAULT 'v1'")
    if "artifact_id" not in existing_columns:
        statements.append("ALTER TABLE inference_logs ADD COLUMN artifact_id VARCHAR(100)")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


ensure_inference_log_columns()

app.include_router(scoring.router, prefix="/v1", tags=["Scoring"])
app.include_router(batch.router, prefix="/v1", tags=["Batch"])
app.include_router(health.router, prefix="/v1", tags=["Health"])
app.include_router(training.router, prefix="/v1", tags=["Training"])
app.include_router(models.router, prefix="/v1", tags=["Models"])
app.include_router(monitoring.router, prefix="/v1", tags=["Monitoring"])
# app.include_router(audit.router, prefix="/v1", tags=["Audit"])
