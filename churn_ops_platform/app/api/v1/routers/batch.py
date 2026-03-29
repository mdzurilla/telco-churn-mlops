from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.v1.schemas.batch import BatchJobCreateResponse, BatchJobStatusResponse
from app.core.config import settings
from app.core.database import get_db
from app.services.batch_service import BatchService
from app.services.job_service import JobService
import uuid

router = APIRouter()

job_service = JobService()
batch_service = BatchService()


@router.post("/batch-score", response_model=BatchJobCreateResponse, status_code=status.HTTP_202_ACCEPTED)
def create_batch_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> BatchJobCreateResponse:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    job_id = str(uuid.uuid4())
    input_path = settings.batch_input_path / f"{job_id}_{Path(file.filename).name}"

    with open(input_path, "wb") as f:
        f.write(file.file.read())

    job_service.create_job(
        db=db,
        job_id=job_id,
        input_file_path=str(input_path),
        model_name=settings.active_model_name,
        model_version=settings.active_model_version,
    )

    background_tasks.add_task(batch_service.process_batch_job, job_id)

    return BatchJobCreateResponse(
        job_id=job_id,
        status="queued",
        message="Batch scoring job created successfully.",
    )


@router.get("/jobs/{job_id}", response_model=BatchJobStatusResponse)
def get_batch_job(job_id: str, db: Session = Depends(get_db)) -> BatchJobStatusResponse:
    job = job_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    download_url = None
    if job.status == "completed" and job.output_file_path:
        download_url = f"/v1/jobs/{job.job_id}/download"

    return BatchJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        input_file_path=job.input_file_path,
        output_file_path=job.output_file_path,
        rows_total=job.rows_total,
        rows_processed=job.rows_processed,
        model_name=job.model_name,
        model_version=job.model_version,
        error_message=job.error_message,
        download_url = download_url,
    )


@router.get("/jobs/{job_id}/download")
def download_batch_output(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail="Batch job is not completed yet."
        )

    if not job.output_file_path:
        raise HTTPException(
            status_code=404,
            detail="No output file is available for this job."
        )

    output_path = Path(job.output_file_path)

    if not output_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Output file does not exist on disk."
        )

    return FileResponse(
        path=output_path,
        media_type="text/csv",
        filename=output_path.name,
    )