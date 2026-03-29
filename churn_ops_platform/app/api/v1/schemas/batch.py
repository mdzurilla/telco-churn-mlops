from datetime import datetime
from typing import Literal

from pydantic import BaseModel


BatchJobStatus = Literal["queued", "running", "completed", "failed"]


class BatchJobCreateResponse(BaseModel):
    job_id: str
    status: BatchJobStatus
    message: str


class BatchJobStatusResponse(BaseModel):
    job_id: str
    status: BatchJobStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    input_file_path: str
    output_file_path: str | None = None
    rows_total: int | None = None
    rows_processed: int
    model_name: str
    model_version: str
    error_message: str | None = None
    download_url: str | None = None