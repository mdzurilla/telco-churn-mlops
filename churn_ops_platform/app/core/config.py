from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Churn Ops Platform API"
    app_version: str = "1.0.0"

    project_root: Path = Path(".")
    artifacts_dir: Path = Path("artifacts")
    models_dir: Path = Path("artifacts/serving")
    logs_dir: Path = Path("logs")
    metadata_dir: Path = Path("metadata")

    batch_input_dir: Path = Path("data/batch/inputs")
    batch_output_dir: Path = Path("data/batch/outputs")

    active_model_name: str = "churn_hist_gradient_boosting"
    active_model_version: str = "v1"

    model_config = SettingsConfigDict(env_file=".env")

    # -------------------------
    # MODEL ARTIFACT
    # -------------------------
    @property
    def active_model_path(self) -> Path:
        return (
            self.models_dir
            / self.active_model_name
            / self.active_model_version
            / "inference_artifact.joblib"
        )

    # BATCH STORAGE
    @property
    def batch_input_path(self) -> Path:
        self.batch_input_dir.mkdir(parents=True, exist_ok=True)
        return self.batch_input_dir

    @property
    def batch_output_path(self) -> Path:
        self.batch_output_dir.mkdir(parents=True, exist_ok=True)
        return self.batch_output_dir

    # DATABASE
    @property
    def sqlite_db_path(self) -> Path:
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        return self.metadata_dir / "mlops.db"

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.sqlite_db_path.as_posix()}"


settings = Settings()