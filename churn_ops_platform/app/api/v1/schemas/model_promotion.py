from pydantic import BaseModel


class ModelPromotionRequest(BaseModel):
    artifact_id: str


class ModelPromotionResponse(BaseModel):
    api_version: str
    model_name: str
    artifact_id: str
    promoted_at: str
    message: str
