from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException

from app.api.v1.schemas.model_promotion import ModelPromotionResponse
from app.api.v1.schemas.models import ModelArtifactResponse, ModelResponse
from app.core.config import settings
from app.repositories.model_repository import ModelRepository
from app.services.model_registry_service import ModelRegistryService


class ModelService:
    def __init__(self, repository: ModelRepository | None = None):
        self.repository = repository or ModelRepository()

    def list_models(
        self,
        promotion_log_path: Path | None = None,
        api_version: str | None = None,
    ) -> list[ModelResponse]:
        current_api_version = api_version or settings.api_version
        promotion_history = self.repository.read_promotion_history(
            promotion_log_path or settings.model_promotion_log_path
        )

        model_names = self.repository.list_model_names(
            settings.serving_dir,
            settings.challenger_dir,
            settings.archive_dir,
        )
        response: list[ModelResponse] = []

        for model_name in model_names:
            artifacts: list[ModelArtifactResponse] = []
            artifacts.extend(
                self._build_stage_artifacts(
                    root=settings.challenger_dir,
                    stage="challenger",
                    api_version=current_api_version,
                    model_name=model_name,
                    promotion_history=promotion_history,
                )
            )
            artifacts.extend(
                self._build_stage_artifacts(
                    root=settings.archive_dir,
                    stage="archive",
                    api_version=current_api_version,
                    model_name=model_name,
                    promotion_history=promotion_history,
                )
            )

            serving_path = settings.serving_model_path(
                api_version=current_api_version,
                model_name=model_name,
            )
            if serving_path.exists():
                metadata = self.repository.read_metadata(serving_path.parent / "metadata.json")
                artifact_id = metadata.get("artifact_id", "artifact_legacy_v1")
                artifacts.insert(
                    0,
                    ModelArtifactResponse(
                        api_version=current_api_version,
                        artifact_id=artifact_id,
                        stage="serving",
                        artifact_path=str(serving_path),
                        is_active=(
                            model_name == settings.active_model_name
                            and current_api_version == settings.active_model_version
                        ),
                        last_promoted_at=self._get_last_promoted_at(
                            promotion_history,
                            api_version=current_api_version,
                            model_name=model_name,
                            artifact_id=artifact_id,
                        ),
                    ),
                )

            if artifacts:
                response.append(
                    ModelResponse(
                        model_name=model_name,
                        active_api_version=current_api_version,
                        artifacts=artifacts,
                    )
                )

        return response

    def promote_model(
        self,
        model_name: str,
        artifact_id: str,
        env_file_path: Path | None = None,
        promotion_log_path: Path | None = None,
        api_version: str | None = None,
    ) -> ModelPromotionResponse:
        current_api_version = api_version or settings.api_version
        challenger_dir = settings.challenger_model_dir(
            api_version=current_api_version,
            model_name=model_name,
        )
        challenger_artifact_dir = challenger_dir / artifact_id
        challenger_artifact_path = challenger_artifact_dir / "inference_artifact.joblib"
        challenger_metadata_path = challenger_artifact_dir / "metadata.json"

        if not challenger_artifact_path.exists():
            raise HTTPException(status_code=404, detail="Challenger artifact not found.")

        serving_path = settings.serving_model_path(
            api_version=current_api_version,
            model_name=model_name,
        )
        serving_metadata_path = serving_path.parent / "metadata.json"

        if serving_path.exists():
            current_metadata = self.repository.read_metadata(serving_metadata_path)
            current_artifact_id = current_metadata.get("artifact_id", "artifact_legacy_v1")
            archive_dir = settings.archive_model_dir(
                api_version=current_api_version,
                model_name=model_name,
            ) / current_artifact_id
            archive_dir.mkdir(parents=True, exist_ok=True)
            self.repository.copy_file(serving_path, archive_dir / "inference_artifact.joblib")
            if serving_metadata_path.exists():
                self.repository.copy_file(serving_metadata_path, archive_dir / "metadata.json")

        self.repository.copy_file(challenger_artifact_path, serving_path)
        if challenger_metadata_path.exists():
            self.repository.copy_file(challenger_metadata_path, serving_metadata_path)

        settings.active_model_name = model_name
        settings.active_model_version = current_api_version
        self.repository.persist_active_model(
            env_file_path or settings.env_file_path,
            model_name=model_name,
            model_version=current_api_version,
        )

        promoted_at = datetime.now(timezone.utc).isoformat()
        self.repository.append_promotion_event(
            promotion_log_path or settings.model_promotion_log_path,
            api_version=current_api_version,
            model_name=model_name,
            artifact_id=artifact_id,
            promoted_at=promoted_at,
        )
        ModelRegistryService.reset_cache()

        return ModelPromotionResponse(
            api_version=current_api_version,
            model_name=model_name,
            artifact_id=artifact_id,
            promoted_at=promoted_at,
            message="Model promoted successfully.",
        )

    def _build_stage_artifacts(
        self,
        *,
        root: Path,
        stage: str,
        api_version: str,
        model_name: str,
        promotion_history: list[dict],
    ) -> list[ModelArtifactResponse]:
        stage_artifacts: list[ModelArtifactResponse] = []
        artifact_dirs = self.repository.list_artifact_directories(
            root=root,
            api_version=api_version,
            model_name=model_name,
        )

        for artifact_dir in artifact_dirs:
            artifact_path = artifact_dir / "inference_artifact.joblib"
            if not artifact_path.exists():
                continue

            stage_artifacts.append(
                ModelArtifactResponse(
                    api_version=api_version,
                    artifact_id=artifact_dir.name,
                    stage=stage,
                    artifact_path=str(artifact_path),
                    is_active=False,
                    last_promoted_at=self._get_last_promoted_at(
                        promotion_history,
                        api_version=api_version,
                        model_name=model_name,
                        artifact_id=artifact_dir.name,
                    ),
                )
            )

        return stage_artifacts

    @staticmethod
    def _get_last_promoted_at(
        promotion_history: list[dict],
        *,
        api_version: str,
        model_name: str,
        artifact_id: str,
    ) -> str | None:
        matching_events = [
            event["promoted_at"]
            for event in promotion_history
            if event.get("api_version", settings.api_version) == api_version
            and event.get("model_name") == model_name
            and (
                event.get("artifact_id") == artifact_id
                or event.get("model_version") == artifact_id
            )
        ]
        return matching_events[-1] if matching_events else None
