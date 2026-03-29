import logging

from sqlalchemy.orm import Session

from app.repositories.audit_repository import AuditRepository


logger = logging.getLogger(__name__)


class AuditService:
    def __init__(self, repository: AuditRepository | None = None):
        self.repository = repository or AuditRepository()

    def log_inference(
        self,
        db: Session,
        *,
        request_source: str,
        request_payload: dict,
        api_version: str = "v1",
        model_name: str,
        model_version: str,
        artifact_id: str | None = None,
        status: str,
        prediction: int | None = None,
        probability: float | None = None,
        threshold: float | None = None,
        error_message: str | None = None,
        job_id: str | None = None,
        row_index: int | None = None,
    ) -> None:
        try:
            self.repository.create_log(
                db,
                request_source=request_source,
                request_payload=request_payload,
                api_version=api_version,
                model_name=model_name,
                model_version=model_version,
                artifact_id=artifact_id,
                status=status,
                prediction=prediction,
                probability=probability,
                threshold=threshold,
                error_message=error_message,
                job_id=job_id,
                row_index=row_index,
            )
        except Exception:
            db.rollback()
            logger.exception("Failed to persist inference audit log.")
