import joblib
from app.core.config import settings


class ModelRegistryService:
    _artifact = None
    _artifact_key = None

    def get_active_artifact(self):
        active_key = (
            settings.api_version,
            settings.active_model_name,
            settings.active_model_version,
        )
        if self.__class__._artifact is None or self.__class__._artifact_key != active_key:
            self.__class__._artifact = joblib.load(settings.active_model_path)
            self.__class__._artifact_key = active_key
        return self.__class__._artifact

    def get_archived_artifact(
        self,
        artifact_id: str,
        *,
        model_name: str | None = None,
        api_version: str | None = None,
    ):
        current_model_name = model_name or settings.active_model_name
        current_api_version = api_version or settings.api_version
        artifact_path = (
            settings.archive_model_dir(
                api_version=current_api_version,
                model_name=current_model_name,
            )
            / artifact_id
            / "inference_artifact.joblib"
        )
        if not artifact_path.exists():
            raise FileNotFoundError(
                f"Archived artifact '{artifact_id}' was not found for model '{current_model_name}'."
            )
        return joblib.load(artifact_path)

    @classmethod
    def reset_cache(cls) -> None:
        cls._artifact = None
        cls._artifact_key = None
