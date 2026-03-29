from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    job_id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    input_file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    output_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    rows_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rows_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)