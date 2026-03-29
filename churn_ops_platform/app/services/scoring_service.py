import polars as pl

from app.services.model_registry_service import ModelRegistryService
from app.utils.feature_transformer import apply_artifacts
from app.utils.inference_preparation import prepare_tree_features_for_inference


class ScoringService:
    def __init__(self, registry_service: ModelRegistryService):
        self.registry_service = registry_service

    def score_one(self, payload: dict) -> dict:
        artifact = self.registry_service.get_active_artifact()
        return self._score_with_artifact(payload, artifact)

    def score_one_historical(self, payload: dict, artifact_id: str) -> dict:
        artifact = self.registry_service.get_archived_artifact(artifact_id)
        return self._score_with_artifact(payload, artifact)

    def _score_with_artifact(self, payload: dict, artifact: dict) -> dict:
        raw_df = pl.DataFrame([payload])

        transformed_df = apply_artifacts(
            raw_df,
            artifact["feature_engineering_artifacts"],
        )

        X = prepare_tree_features_for_inference(
            df=transformed_df,
            categorical_cols=artifact["categorical_cols"],
            numerical_cols=artifact["numerical_cols"],
            categorical_orders=artifact.get("categorical_orders"),
            reference_columns=artifact["reference_columns"],
        )

        probability = float(artifact["model"].predict_proba(X)[:, 1][0])
        prediction = int(probability >= artifact["threshold"])

        return {
            "api_version": artifact.get("api_version", "v1"),
            "model_name": artifact["model_name"],
            "model_version": artifact["model_version"],
            "artifact_id": artifact.get("artifact_id", "artifact_legacy_v1"),
            "probability": probability,
            "prediction": prediction,
            "threshold": artifact["threshold"],
        }
