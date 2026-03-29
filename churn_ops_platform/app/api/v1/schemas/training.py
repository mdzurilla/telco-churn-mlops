from pydantic import BaseModel


class ClassificationMetricsResponse(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1: float
    auc: float | None
    pr_auc: float | None
    tp: int
    tn: int
    fp: int
    fn: int


class RetrainComparisonResponse(BaseModel):
    serving: ClassificationMetricsResponse
    challenger: ClassificationMetricsResponse


class RetrainResponse(BaseModel):
    api_version: str
    model_name: str
    model_version: str
    artifact_id: str
    trained_at: str
    threshold: float
    rows_received: int
    train_rows: int
    eval_rows: int
    challenger_metrics: ClassificationMetricsResponse
    comparison_to_serving: RetrainComparisonResponse
