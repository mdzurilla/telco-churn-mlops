import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np

from app.services.model_registry_service import ModelRegistryService
from app.services.scoring_service import ScoringService


class DummyModel:
    def predict_proba(self, X):
        rows = len(X)
        positive = np.full(rows, 0.72)
        negative = 1 - positive
        return np.column_stack([negative, positive])


class HistoricalScoringTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path("tests") / "_tmp" / f"historical-score-{uuid.uuid4().hex}"
        self.archive_dir = self.temp_root / "archive"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_score_one_historical_uses_archived_artifact(self) -> None:
        artifact_id = "artifact_test_archive"
        artifact_dir = self.archive_dir / "v1" / "churn_hist_gradient_boosting" / artifact_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(
            {
                "api_version": "v1",
                "model_name": "churn_hist_gradient_boosting",
                "model_version": "v1",
                "artifact_id": artifact_id,
                "model": DummyModel(),
                "categorical_cols": [
                    "gender",
                    "Partner",
                    "Dependents",
                    "PhoneService",
                    "MultipleLines",
                    "InternetService",
                    "OnlineSecurity",
                    "OnlineBackup",
                    "DeviceProtection",
                    "TechSupport",
                    "StreamingTV",
                    "StreamingMovies",
                    "Contract",
                    "PaperlessBilling",
                    "PaymentMethod",
                ],
                "numerical_cols": [
                    "SeniorCitizen",
                    "tenure",
                    "MonthlyCharges",
                    "TotalCharges",
                ],
                "categorical_orders": {},
                "reference_columns": [
                    "gender_Female",
                    "gender_Male",
                    "Partner_No",
                    "Partner_Yes",
                    "Dependents_No",
                    "Dependents_Yes",
                    "PhoneService_No",
                    "PhoneService_Yes",
                    "MultipleLines_No",
                    "MultipleLines_No phone service",
                    "MultipleLines_Yes",
                    "InternetService_DSL",
                    "InternetService_Fiber optic",
                    "InternetService_No",
                    "OnlineSecurity_No",
                    "OnlineSecurity_No internet service",
                    "OnlineSecurity_Yes",
                    "OnlineBackup_No",
                    "OnlineBackup_No internet service",
                    "OnlineBackup_Yes",
                    "DeviceProtection_No",
                    "DeviceProtection_No internet service",
                    "DeviceProtection_Yes",
                    "TechSupport_No",
                    "TechSupport_No internet service",
                    "TechSupport_Yes",
                    "StreamingTV_No",
                    "StreamingTV_No internet service",
                    "StreamingTV_Yes",
                    "StreamingMovies_No",
                    "StreamingMovies_No internet service",
                    "StreamingMovies_Yes",
                    "Contract_Month-to-month",
                    "Contract_One year",
                    "Contract_Two year",
                    "PaperlessBilling_No",
                    "PaperlessBilling_Yes",
                    "PaymentMethod_Bank transfer (automatic)",
                    "PaymentMethod_Credit card (automatic)",
                    "PaymentMethod_Electronic check",
                    "PaymentMethod_Mailed check",
                    "SeniorCitizen",
                    "tenure",
                    "MonthlyCharges",
                    "TotalCharges",
                ],
                "feature_engineering_artifacts": [],
                "threshold": 0.31,
            },
            artifact_dir / "inference_artifact.joblib",
        )

        scoring_service = ScoringService(ModelRegistryService())
        payload = {
            "customerID": "abc-123",
            "gender": "Female",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 24,
            "PhoneService": "Yes",
            "MultipleLines": "No",
            "InternetService": "DSL",
            "OnlineSecurity": "Yes",
            "OnlineBackup": "No",
            "DeviceProtection": "Yes",
            "TechSupport": "No",
            "StreamingTV": "Yes",
            "StreamingMovies": "No",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 75.5,
            "TotalCharges": 1812.0,
        }

        with patch("app.services.model_registry_service.settings.archive_dir", self.archive_dir):
            result = scoring_service.score_one_historical(payload, artifact_id)

        self.assertEqual(result["artifact_id"], artifact_id)
        self.assertEqual(result["model_name"], "churn_hist_gradient_boosting")
        self.assertEqual(result["prediction"], 1)
        self.assertAlmostEqual(result["probability"], 0.72)


if __name__ == "__main__":
    unittest.main()
