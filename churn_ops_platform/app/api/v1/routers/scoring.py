from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.schemas.scoring import ScoreRequest, ScoreResponse
from app.core.database import get_db
from app.services.audit_service import AuditService
from app.services.model_registry_service import ModelRegistryService
from app.services.scoring_service import ScoringService

router = APIRouter()

model_registry_service = ModelRegistryService()
scoring_service = ScoringService(model_registry_service)
audit_service = AuditService()


@router.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest, db: Session = Depends(get_db)) -> ScoreResponse:
    result = scoring_service.score_one(payload.model_dump())
    audit_service.log_inference(
        db,
        request_source="realtime",
        request_payload=payload.model_dump(),
        api_version=result["api_version"],
        model_name=result["model_name"],
        model_version=result["model_version"],
        artifact_id=result["artifact_id"],
        status="success",
        prediction=result["prediction"],
        probability=result["probability"],
        threshold=result["threshold"],
    )
    return ScoreResponse(**result)


@router.post("/score/historical/{artifact_id}", response_model=ScoreResponse)
def score_historical(
    artifact_id: str,
    payload: ScoreRequest,
    db: Session = Depends(get_db),
) -> ScoreResponse:
    try:
        result = scoring_service.score_one_historical(payload.model_dump(), artifact_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    audit_service.log_inference(
        db,
        request_source="historical",
        request_payload=payload.model_dump(),
        api_version=result["api_version"],
        model_name=result["model_name"],
        model_version=result["model_version"],
        artifact_id=result["artifact_id"],
        status="success",
        prediction=result["prediction"],
        probability=result["probability"],
        threshold=result["threshold"],
    )
    return ScoreResponse(**result)
