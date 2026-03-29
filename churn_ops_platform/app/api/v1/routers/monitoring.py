from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.schemas.monitoring import MonitoringSummaryResponse
from app.core.database import get_db
from app.services.monitoring_service import MonitoringService

router = APIRouter()

monitoring_service = MonitoringService()


@router.get("/monitoring/summary", response_model=MonitoringSummaryResponse)
def get_monitoring_summary(db: Session = Depends(get_db)) -> MonitoringSummaryResponse:
    return monitoring_service.get_summary(db)
