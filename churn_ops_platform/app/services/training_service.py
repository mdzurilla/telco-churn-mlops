import json
import os
from io import BytesIO
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
import polars as pl
from sklearn.ensemble._hist_gradient_boosting import binning as hgb_binning
from sklearn.ensemble._hist_gradient_boosting import gradient_boosting as hgb_gradient_boosting
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import train_test_split

from app.api.v1.schemas.training import (
    ClassificationMetricsResponse,
    RetrainComparisonResponse,
    RetrainResponse,
)
from app.core.config import settings
from app.services.model_registry_service import ModelRegistryService
from app.utils.feature_transformer import apply_artifacts
from app.utils.inference_preparation import prepare_tree_features_for_inference


class TrainingService:
    target_col = "Churn"

    def retrain_from_csv(self, csv_bytes: bytes, filename: str | None = None) -> RetrainResponse:
        os.environ.setdefault("OMP_NUM_THREADS", "1")
        os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
        df = pd.read_csv(BytesIO(csv_bytes))
        if self.target_col not in df.columns:
            raise ValueError(f"Training dataset must include target column '{self.target_col}'.")

        artifact_id = self._generate_artifact_id()
        trained_at = datetime.now(timezone.utc).isoformat()

        source_bundle = joblib.load(settings.source_model_bundle_path)
        feature_artifacts = self._load_feature_artifacts(settings.source_feature_artifacts_dir)

        train_df, eval_df = train_test_split(
            df,
            test_size=0.3,
            random_state=42,
            stratify=df[self.target_col],
        )

        X_train, y_train = self._prepare_training_data(
            train_df,
            source_bundle=source_bundle,
            feature_artifacts=feature_artifacts,
            reference_columns=None,
        )
        X_eval_challenger, y_eval = self._prepare_training_data(
            eval_df,
            source_bundle=source_bundle,
            feature_artifacts=feature_artifacts,
            reference_columns=X_train.columns.tolist(),
        )

        base_model = source_bundle.get("model")
        model = clone(base_model) if base_model is not None else HistGradientBoostingClassifier(random_state=42)
        with ExitStack() as stack:
            stack.enter_context(
                patch.object(hgb_gradient_boosting, "_openmp_effective_n_threads", lambda *args, **kwargs: 1)
            )
            stack.enter_context(
                patch.object(hgb_binning, "_openmp_effective_n_threads", lambda *args, **kwargs: 1)
            )
            model.fit(X_train, y_train)

            challenger_prob = model.predict_proba(X_eval_challenger)[:, 1]
            threshold_results = self._evaluate_thresholds(y_eval, challenger_prob)
            best_threshold_row = threshold_results.sort_values(
                by=["f1", "pr_auc", "recall", "precision"],
                ascending=[False, False, False, False],
            ).iloc[0]
            threshold = float(best_threshold_row["threshold"])
            challenger_pred = (challenger_prob >= threshold).astype(int)
            challenger_metrics = self._compute_classification_metrics(
                y_true=y_eval,
                y_pred=challenger_pred,
                y_prob=challenger_prob,
            )

            serving_artifact = ModelRegistryService().get_active_artifact()
            X_eval_serving, _ = self._prepare_training_data(
                eval_df,
                source_bundle=source_bundle,
                feature_artifacts=feature_artifacts,
                reference_columns=serving_artifact["reference_columns"],
            )
            serving_prob = serving_artifact["model"].predict_proba(X_eval_serving)[:, 1]
            serving_pred = (serving_prob >= serving_artifact["threshold"]).astype(int)
            serving_metrics = self._compute_classification_metrics(
                y_true=y_eval,
                y_pred=serving_pred,
                y_prob=serving_prob,
            )

        challenger_artifact = {
            "api_version": settings.api_version,
            "model_name": settings.active_model_name,
            "model_version": settings.active_model_version,
            "artifact_id": artifact_id,
            "trained_at": trained_at,
            "model_family": type(model).__name__,
            "model": model,
            "categorical_cols": source_bundle["categorical_cols"],
            "numerical_cols": source_bundle["numerical_cols"],
            "categorical_orders": source_bundle.get("categorical_orders"),
            "reference_columns": X_train.columns.tolist(),
            "feature_engineering_artifacts": feature_artifacts,
            "threshold": threshold,
            "training_metrics": challenger_metrics,
        }

        challenger_dir = settings.challenger_model_dir(
            api_version=settings.api_version,
            model_name=settings.active_model_name,
        ) / artifact_id
        challenger_dir.mkdir(parents=True, exist_ok=True)
        artifact_path = challenger_dir / "inference_artifact.joblib"
        metadata_path = challenger_dir / "metadata.json"

        joblib.dump(challenger_artifact, artifact_path)
        metadata_path.write_text(
            json.dumps(
                {
                    "api_version": settings.api_version,
                    "model_name": settings.active_model_name,
                    "model_version": settings.active_model_version,
                    "artifact_id": artifact_id,
                    "trained_at": trained_at,
                    "threshold": threshold,
                    "source_filename": filename,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        return RetrainResponse(
            api_version=settings.api_version,
            model_name=settings.active_model_name,
            model_version=settings.active_model_version,
            artifact_id=artifact_id,
            trained_at=trained_at,
            threshold=threshold,
            rows_received=len(df),
            train_rows=len(train_df),
            eval_rows=len(eval_df),
            challenger_metrics=ClassificationMetricsResponse(**challenger_metrics),
            comparison_to_serving=RetrainComparisonResponse(
                serving=ClassificationMetricsResponse(**serving_metrics),
                challenger=ClassificationMetricsResponse(**challenger_metrics),
            ),
        )

    def _prepare_training_data(
        self,
        df: pd.DataFrame,
        *,
        source_bundle: dict,
        feature_artifacts: list[dict],
        reference_columns: list[str] | None,
    ) -> tuple[pd.DataFrame, np.ndarray]:
        raw_features = df.drop(columns=[self.target_col])
        transformed_df = apply_artifacts(pl.from_pandas(raw_features), feature_artifacts)
        X = prepare_tree_features_for_inference(
            df=transformed_df,
            categorical_cols=source_bundle["categorical_cols"],
            numerical_cols=source_bundle["numerical_cols"],
            categorical_orders=source_bundle.get("categorical_orders"),
            reference_columns=reference_columns,
        )
        y = self._normalize_target(df[self.target_col])
        return X, y

    def _load_feature_artifacts(self, directory: Path) -> list[dict]:
        artifacts: list[dict] = []
        for file_path in sorted(directory.glob("*.json")):
            artifacts.append(json.loads(file_path.read_text(encoding="utf-8")))
        return artifacts

    def _normalize_target(self, series: pd.Series) -> np.ndarray:
        values = series.astype(str).str.strip().str.lower()
        mapped = values.map({"yes": 1, "no": 0, "1": 1, "0": 0})
        if mapped.isna().any():
            raise ValueError("Target column must contain binary values like Yes/No or 1/0.")
        return mapped.astype(int).to_numpy()

    def _generate_artifact_id(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
        return f"artifact_{timestamp}_{uuid4().hex[:8]}"

    def _compute_classification_metrics(
        self,
        *,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_prob: np.ndarray | None = None,
    ) -> dict:
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())

        accuracy = (tp + tn) / len(y_true)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        auc = None
        pr_auc = None
        if y_prob is not None:
            auc = float(roc_auc_score(y_true, y_prob))
            pr_auc = float(average_precision_score(y_true, y_prob))

        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "auc": auc,
            "pr_auc": pr_auc,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
        }

    def _evaluate_thresholds(
        self,
        y_true: np.ndarray,
        y_prob: np.ndarray,
        thresholds: np.ndarray | None = None,
    ) -> pd.DataFrame:
        if thresholds is None:
            thresholds = np.linspace(0.01, 0.99, 99)

        pr_auc = float(average_precision_score(y_true, y_prob))
        auc = float(roc_auc_score(y_true, y_prob))

        results: list[dict] = []
        for threshold in thresholds:
            y_pred = (y_prob >= threshold).astype(int)
            metrics = self._compute_classification_metrics(y_true=y_true, y_pred=y_pred, y_prob=None)
            results.append(
                {
                    "threshold": float(threshold),
                    "accuracy": metrics["accuracy"],
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1": metrics["f1"],
                    "tp": metrics["tp"],
                    "tn": metrics["tn"],
                    "fp": metrics["fp"],
                    "fn": metrics["fn"],
                    "auc": auc,
                    "pr_auc": pr_auc,
                }
            )

        return pd.DataFrame(results)
