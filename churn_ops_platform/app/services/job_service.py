from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.batch_job import BatchJob


class JobService:
    def create_job(
        self,
        db: Session,
        job_id: str,
        input_file_path: str,
        model_name: str,
        model_version: str,
    ) -> BatchJob:
        job = BatchJob(
            job_id=job_id,
            status="queued",
            input_file_path=input_file_path,
            model_name=model_name,
            model_version=model_version,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    def get_job(self, db: Session, job_id: str) -> BatchJob | None:
        return db.query(BatchJob).filter(BatchJob.job_id == job_id).first()

    def mark_running(self, db: Session, job_id: str) -> None:
        job = self.get_job(db, job_id)
        if job is None:
            return
        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        db.commit()

    def update_progress(
        self,
        db: Session,
        job_id: str,
        rows_total: int | None = None,
        rows_processed: int | None = None,
    ) -> None:
        job = self.get_job(db, job_id)
        if job is None:
            return
        if rows_total is not None:
            job.rows_total = rows_total
        if rows_processed is not None:
            job.rows_processed = rows_processed
        db.commit()

    def mark_completed(
        self,
        db: Session,
        job_id: str,
        output_file_path: str,
        rows_total: int,
        rows_processed: int,
    ) -> None:
        job = self.get_job(db, job_id)
        if job is None:
            return
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        job.output_file_path = output_file_path
        job.rows_total = rows_total
        job.rows_processed = rows_processed
        db.commit()

    def mark_failed(
        self,
        db: Session,
        job_id: str,
        error_message: str,
        rows_total: int | None = None,
        rows_processed: int = 0,
    ) -> None:
        job = self.get_job(db, job_id)
        if job is None:
            return
        job.status = "failed"
        job.completed_at = datetime.now(timezone.utc)
        job.rows_total = rows_total
        job.rows_processed = rows_processed
        job.error_message = error_message
        db.commit()