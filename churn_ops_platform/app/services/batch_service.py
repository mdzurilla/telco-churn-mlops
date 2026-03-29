from pathlib import Path
import logging

import pandas as pd

from pydantic import ValidationError

from app.api.v1.schemas.scoring import ScoreRequest
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.audit_service import AuditService
from app.services.job_service import JobService
from app.services.model_registry_service import ModelRegistryService
from app.services.scoring_service import ScoringService


logger = logging.getLogger(__name__)


class BatchService:
    def __init__(self):
        self.job_service = JobService()
        self.registry_service = ModelRegistryService()
        self.scoring_service = ScoringService(self.registry_service)
        self.audit_service = AuditService()

    def process_batch_job(self, job_id: str) -> None:
        db = SessionLocal()

        try:
            job = self.job_service.get_job(db, job_id)
            if job is None:
                logger.error("Batch job %s not found.", job_id)
                return

            self.job_service.mark_running(db, job_id)
            logger.info("Batch job %s marked as running.", job_id)

            input_path = Path(job.input_file_path)
            df = pd.read_csv(input_path)

            rows_total = len(df)
            self.job_service.update_progress(
                db,
                job_id,
                rows_total=rows_total,
                rows_processed=0,
            )

            output_rows: list[dict] = []

            for idx, row in df.iterrows():
                raw_record = row.to_dict()

                try:
                    validated = ScoreRequest(**raw_record)
                    result = self.scoring_service.score_one(validated.model_dump())
                    self.audit_service.log_inference(
                        db,
                        request_source="batch",
                        request_payload=validated.model_dump(),
                        api_version=result["api_version"],
                        model_name=result["model_name"],
                        model_version=result["model_version"],
                        artifact_id=result["artifact_id"],
                        status="success",
                        prediction=result["prediction"],
                        probability=result["probability"],
                        threshold=result["threshold"],
                        job_id=job_id,
                        row_index=idx,
                    )

                    output_row = {
                        **raw_record,
                        "row_status": "success",
                        "row_error": None,
                        "score_probability": result["probability"],
                        "prediction": result["prediction"],
                        "threshold": result["threshold"],
                        "model_name": result["model_name"],
                        "model_version": result["model_version"],
                        "artifact_id": result["artifact_id"],
                    }

                except ValidationError as exc:
                    error_message = self._format_validation_error(exc)
                    self.audit_service.log_inference(
                        db,
                        request_source="batch",
                        request_payload=raw_record,
                        api_version=settings.api_version,
                        model_name=settings.active_model_name,
                        model_version=settings.active_model_version,
                        artifact_id=None,
                        status="validation_error",
                        error_message=error_message,
                        job_id=job_id,
                        row_index=idx,
                    )
                    output_row = {
                        **raw_record,
                        "row_status": "validation_error",
                        "row_error": error_message,
                        "score_probability": None,
                        "prediction": None,
                        "threshold": None,
                        "model_name": settings.active_model_name,
                        "model_version": settings.active_model_version,
                        "artifact_id": None,
                    }

                except Exception as exc:
                    logger.exception(
                        "Unexpected row scoring error in job %s at row %s.",
                        job_id,
                        idx,
                    )
                    self.audit_service.log_inference(
                        db,
                        request_source="batch",
                        request_payload=raw_record,
                        api_version=settings.api_version,
                        model_name=settings.active_model_name,
                        model_version=settings.active_model_version,
                        artifact_id=None,
                        status="scoring_error",
                        error_message=str(exc),
                        job_id=job_id,
                        row_index=idx,
                    )
                    output_row = {
                        **raw_record,
                        "row_status": "scoring_error",
                        "row_error": str(exc),
                        "score_probability": None,
                        "prediction": None,
                        "threshold": None,
                        "model_name": settings.active_model_name,
                        "model_version": settings.active_model_version,
                        "artifact_id": None,
                    }

                output_rows.append(output_row)

                self.job_service.update_progress(
                    db,
                    job_id,
                    rows_processed=idx + 1,
                )

            output_df = pd.DataFrame(output_rows)

            output_path = (
                settings.batch_output_path
                / f"{job_id}_scored_output.csv"
            )
            output_df.to_csv(output_path, index=False)

            self.job_service.mark_completed(
                db,
                job_id=job_id,
                output_file_path=str(output_path),
                rows_total=rows_total,
                rows_processed=rows_total,
            )

            logger.info("Batch job %s completed successfully.", job_id)

        except Exception as exc:
            logger.exception("Batch job %s failed.", job_id)
            self.job_service.mark_failed(
                db,
                job_id=job_id,
                error_message=str(exc),
            )
        finally:
            db.close()

    @staticmethod
    def _format_validation_error(exc: ValidationError) -> str:
        parts = []
        for err in exc.errors():
            location = ".".join(str(x) for x in err.get("loc", []))
            message = err.get("msg", "Validation error")
            parts.append(f"{location}: {message}")
        return "; ".join(parts)
