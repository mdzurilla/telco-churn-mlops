from fastapi import APIRouter
from app.api.v1.schemas.scoring import ScoreRequest, ScoreResponse
from app.services.model_registry_service import ModelRegistryService
from app.services.scoring_service import ScoringService

router = APIRouter()

model_registry_service = ModelRegistryService()
scoring_service = ScoringService(model_registry_service)


@router.post("/score", response_model=ScoreResponse)
def score(payload: ScoreRequest) -> ScoreResponse:
    result = scoring_service.score_one(payload.model_dump())
    return ScoreResponse(**result)