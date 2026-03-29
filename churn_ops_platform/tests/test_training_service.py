import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from app.services.training_service import TrainingService


class TrainingServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path("tests") / "_tmp" / f"training-service-{uuid.uuid4().hex}"
        self.challenger_dir = self.temp_root / "challenger"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def test_retrain_from_csv_creates_challenger_artifact(self) -> None:
        rows: list[dict] = []
        for idx in range(12):
            rows.append(
                {
                    "customerID": f"YES-{idx}",
                    "gender": "Female",
                    "SeniorCitizen": 0,
                    "Partner": "No",
                    "Dependents": "No",
                    "tenure": 2 + idx,
                    "PhoneService": "Yes",
                    "MultipleLines": "No",
                    "InternetService": "Fiber optic",
                    "OnlineSecurity": "No",
                    "OnlineBackup": "No",
                    "DeviceProtection": "No",
                    "TechSupport": "No",
                    "StreamingTV": "Yes",
                    "StreamingMovies": "Yes",
                    "Contract": "Month-to-month",
                    "PaperlessBilling": "Yes",
                    "PaymentMethod": "Electronic check",
                    "MonthlyCharges": 85.0,
                    "TotalCharges": 170.0 + idx,
                    "Churn": "Yes",
                }
            )
            rows.append(
                {
                    "customerID": f"NO-{idx}",
                    "gender": "Male",
                    "SeniorCitizen": 0,
                    "Partner": "Yes",
                    "Dependents": "Yes",
                    "tenure": 50 + idx,
                    "PhoneService": "Yes",
                    "MultipleLines": "Yes",
                    "InternetService": "DSL",
                    "OnlineSecurity": "Yes",
                    "OnlineBackup": "Yes",
                    "DeviceProtection": "Yes",
                    "TechSupport": "Yes",
                    "StreamingTV": "No",
                    "StreamingMovies": "No",
                    "Contract": "Two year",
                    "PaperlessBilling": "No",
                    "PaymentMethod": "Bank transfer (automatic)",
                    "MonthlyCharges": 55.0,
                    "TotalCharges": 2750.0 + idx,
                    "Churn": "No",
                }
            )

        csv_bytes = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
        service = TrainingService()

        with patch("app.services.training_service.settings.challenger_dir", self.challenger_dir):
            result = service.retrain_from_csv(csv_bytes, filename="retrain.csv")

        artifact_dir = self.challenger_dir / "v1" / "churn_hist_gradient_boosting" / result.artifact_id
        self.assertTrue((artifact_dir / "inference_artifact.joblib").exists())
        self.assertTrue((artifact_dir / "metadata.json").exists())
        self.assertEqual(result.api_version, "v1")
        self.assertEqual(result.model_name, "churn_hist_gradient_boosting")
        self.assertEqual(result.rows_received, 24)
        self.assertGreater(result.threshold, 0.0)
        self.assertLess(result.threshold, 1.0)


if __name__ == "__main__":
    unittest.main()
