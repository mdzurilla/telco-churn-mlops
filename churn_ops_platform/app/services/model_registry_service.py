import joblib
from app.core.config import settings


class ModelRegistryService:
    def __init__(self):
        self._artifact = None

    def get_active_artifact(self):
        if self._artifact is None:
            self._artifact = joblib.load(settings.active_model_path)
        return self._artifact