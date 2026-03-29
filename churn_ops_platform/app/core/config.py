from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Churn Ops Platform API"
    app_version: str = "1.0.0"
    api_version: str = "v1"

    project_root: Path = Path(".")
    artifacts_dir: Path = Path("artifacts")
    serving_dir: Path = Path("artifacts/serving")
    challenger_dir: Path = Path("artifacts/challenger")
    archive_dir: Path = Path("artifacts/archive")
    source_model_bundles_dir: Path = Path("artifacts/source/model_bundles")
    source_feature_artifacts_dir: Path = Path("artifacts/source/feature_engineering")
    logs_dir: Path = Path("logs")
    metadata_dir: Path = Path("metadata")

    batch_input_dir: Path = Path("data/batch/inputs")
    batch_output_dir: Path = Path("data/batch/outputs")

    active_model_name: str = "churn_hist_gradient_boosting"
    active_model_version: str = "v1"

    model_config = SettingsConfigDict(env_file=".env")

    # MODEL ARTIFACT
    @property
    def active_model_path(self) -> Path:
        serving_path = self.serving_model_path(
            api_version=self.api_version,
            model_name=self.active_model_name,
        )
        if serving_path.exists():
            return serving_path

        return (
            self.serving_dir
            / self.active_model_name
            / self.active_model_version
            / "inference_artifact.joblib"
        )

    def serving_model_dir(self, *, api_version: str, model_name: str) -> Path:
        path = self.serving_dir / api_version / model_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def serving_model_path(self, *, api_version: str, model_name: str) -> Path:
        return self.serving_model_dir(
            api_version=api_version,
            model_name=model_name,
        ) / "inference_artifact.joblib"

    def challenger_model_dir(self, *, api_version: str, model_name: str) -> Path:
        path = self.challenger_dir / api_version / model_name
        path.mkdir(parents=True, exist_ok=True)
        return path

    def archive_model_dir(self, *, api_version: str, model_name: str) -> Path:
        path = self.archive_dir / api_version / model_name
        path.mkdir(parents=True, exist_ok=True)
        return path

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

    @property
    def env_file_path(self) -> Path:
        return Path(".env")

    @property
    def model_promotion_log_path(self) -> Path:
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        return self.metadata_dir / "model_promotions.json"

    @property
    def source_model_bundle_path(self) -> Path:
        return self.source_model_bundles_dir / "hist_boosted_trees_final.pkl"


settings = Settings()
