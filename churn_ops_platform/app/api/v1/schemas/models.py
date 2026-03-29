from pydantic import BaseModel


class ModelArtifactResponse(BaseModel):
    api_version: str
    artifact_id: str
    stage: str
    artifact_path: str
    is_active: bool
    last_promoted_at: str | None = None


class ModelResponse(BaseModel):
    model_name: str
    active_api_version: str
    artifacts: list[ModelArtifactResponse]
