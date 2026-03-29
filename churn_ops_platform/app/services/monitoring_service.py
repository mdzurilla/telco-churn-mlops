from datetime import datetime, timedelta, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.v1.schemas.monitoring import (
    MonitoringPredictionDistribution,
    MonitoringSourceBreakdown,
    MonitoringStatusBreakdown,
    MonitoringSummaryResponse,
    MonitoringTrendPoint,
)
from app.models.inference_log import InferenceLog


class MonitoringService:
    def get_summary(self, db: Session) -> MonitoringSummaryResponse:
        total_requests = db.query(func.count(InferenceLog.id)).scalar() or 0

        successful_predictions = (
            db.query(func.count(InferenceLog.id))
            .filter(InferenceLog.status == "success")
            .scalar()
            or 0
        )

        average_probability = (
            db.query(func.avg(InferenceLog.probability))
            .filter(InferenceLog.status == "success")
            .scalar()
        )

        prediction_0 = (
            db.query(func.count(InferenceLog.id))
            .filter(
                InferenceLog.status == "success",
                InferenceLog.prediction == 0,
            )
            .scalar()
            or 0
        )
        prediction_1 = (
            db.query(func.count(InferenceLog.id))
            .filter(
                InferenceLog.status == "success",
                InferenceLog.prediction == 1,
            )
            .scalar()
            or 0
        )

        success_count = successful_predictions
        validation_error_count = (
            db.query(func.count(InferenceLog.id))
            .filter(InferenceLog.status == "validation_error")
            .scalar()
            or 0
        )
        scoring_error_count = (
            db.query(func.count(InferenceLog.id))
            .filter(InferenceLog.status == "scoring_error")
            .scalar()
            or 0
        )

        realtime_count = (
            db.query(func.count(InferenceLog.id))
            .filter(InferenceLog.request_source == "realtime")
            .scalar()
            or 0
        )
        batch_count = (
            db.query(func.count(InferenceLog.id))
            .filter(InferenceLog.request_source == "batch")
            .scalar()
            or 0
        )

        trend_rows = self._get_daily_volume_last_7_days(db)

        return MonitoringSummaryResponse(
            total_requests=total_requests,
            successful_predictions=successful_predictions,
            average_probability=(
                round(float(average_probability), 4)
                if average_probability is not None
                else None
            ),
            prediction_distribution=MonitoringPredictionDistribution(
                prediction_0=prediction_0,
                prediction_1=prediction_1,
            ),
            status_breakdown=MonitoringStatusBreakdown(
                success=success_count,
                validation_error=validation_error_count,
                scoring_error=scoring_error_count,
            ),
            source_breakdown=MonitoringSourceBreakdown(
                realtime=realtime_count,
                batch=batch_count,
            ),
            daily_volume_last_7_days=trend_rows,
        )

    def _get_daily_volume_last_7_days(self, db: Session) -> list[MonitoringTrendPoint]:
        today = datetime.now(timezone.utc).date()
        start_date = today - timedelta(days=6)

        rows = (
            db.query(
                func.date(InferenceLog.created_at).label("day"),
                func.count(InferenceLog.id).label("request_count"),
            )
            .filter(InferenceLog.created_at >= start_date)
            .group_by(func.date(InferenceLog.created_at))
            .order_by(func.date(InferenceLog.created_at))
            .all()
        )

        counts_by_day = {str(row.day): row.request_count for row in rows}

        return [
            MonitoringTrendPoint(
                date=day.isoformat(),
                request_count=counts_by_day.get(day.isoformat(), 0),
            )
            for day in (start_date + timedelta(days=offset) for offset in range(7))
        ]
