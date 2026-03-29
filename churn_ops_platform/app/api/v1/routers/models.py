from fastapi import APIRouter

from app.api.v1.schemas.model_promotion import (
    ModelPromotionRequest,
    ModelPromotionResponse,
)
from app.api.v1.schemas.models import ModelResponse
from app.services.model_service import ModelService

router = APIRouter()

model_service = ModelService()


@router.get("/models", response_model=list[ModelResponse])
def list_models() -> list[ModelResponse]:
    return model_service.list_models()


@router.post("/models/{model_name}/promote", response_model=ModelPromotionResponse)
def promote_model(
    model_name: str,
    payload: ModelPromotionRequest,
) -> ModelPromotionResponse:
    return model_service.promote_model(model_name, payload.artifact_id)
