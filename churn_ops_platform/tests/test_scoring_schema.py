import unittest

from pydantic import ValidationError

from app.api.v1.schemas.scoring import ScoreRequest


class ScoreRequestTestCase(unittest.TestCase):
    def test_normalizes_common_string_fields(self) -> None:
        payload = {
            "customerID": "abc-123",
            "gender": " female ",
            "SeniorCitizen": 0,
            "Partner": " yes ",
            "Dependents": "no",
            "tenure": 12,
            "PhoneService": "yes",
            "MultipleLines": " no ",
            "InternetService": "dsl",
            "OnlineSecurity": "yes",
            "OnlineBackup": " no ",
            "DeviceProtection": "yes",
            "TechSupport": " no ",
            "StreamingTV": "yes",
            "StreamingMovies": "no",
            "Contract": " month-to-month ",
            "PaperlessBilling": " yes ",
            "PaymentMethod": " electronic check ",
            "MonthlyCharges": 70.5,
            "TotalCharges": 840.0,
        }

        result = ScoreRequest(**payload)

        self.assertEqual(result.gender, "Female")
        self.assertEqual(result.Partner, "Yes")
        self.assertEqual(result.Dependents, "No")
        self.assertEqual(result.InternetService, "DSL")
        self.assertEqual(result.Contract, "Month-to-month")
        self.assertEqual(result.PaymentMethod, "Electronic check")

    def test_rejects_inconsistent_phone_service_combination(self) -> None:
        payload = {
            "customerID": "abc-123",
            "gender": "Male",
            "SeniorCitizen": 0,
            "Partner": "Yes",
            "Dependents": "No",
            "tenure": 12,
            "PhoneService": "No",
            "MultipleLines": "Yes",
            "InternetService": "No",
            "OnlineSecurity": "No internet service",
            "OnlineBackup": "No internet service",
            "DeviceProtection": "No internet service",
            "TechSupport": "No internet service",
            "StreamingTV": "No internet service",
            "StreamingMovies": "No internet service",
            "Contract": "Month-to-month",
            "PaperlessBilling": "Yes",
            "PaymentMethod": "Electronic check",
            "MonthlyCharges": 20.0,
            "TotalCharges": 20.0,
        }

        with self.assertRaises(ValidationError) as ctx:
            ScoreRequest(**payload)

        self.assertIn("MultipleLines must be 'No phone service'", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
