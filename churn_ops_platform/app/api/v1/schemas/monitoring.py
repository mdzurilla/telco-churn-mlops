from pydantic import BaseModel


class MonitoringPredictionDistribution(BaseModel):
    prediction_0: int
    prediction_1: int


class MonitoringStatusBreakdown(BaseModel):
    success: int
    validation_error: int
    scoring_error: int


class MonitoringSourceBreakdown(BaseModel):
    realtime: int
    batch: int


class MonitoringTrendPoint(BaseModel):
    date: str
    request_count: int


class MonitoringSummaryResponse(BaseModel):
    total_requests: int
    successful_predictions: int
    average_probability: float | None
    prediction_distribution: MonitoringPredictionDistribution
    status_breakdown: MonitoringStatusBreakdown
    source_breakdown: MonitoringSourceBreakdown
    daily_volume_last_7_days: list[MonitoringTrendPoint]
