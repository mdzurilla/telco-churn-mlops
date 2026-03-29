import json

from sqlalchemy.orm import Session

from app.models.inference_log import InferenceLog


class AuditRepository:
    def create_log(
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
    ) -> InferenceLog:
        log = InferenceLog(
            request_source=request_source,
            request_payload=json.dumps(request_payload, default=str),
            api_version=api_version,
            prediction=prediction,
            probability=probability,
            threshold=threshold,
            model_name=model_name,
            model_version=model_version,
            artifact_id=artifact_id,
            status=status,
            error_message=error_message,
            job_id=job_id,
            row_index=row_index,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
