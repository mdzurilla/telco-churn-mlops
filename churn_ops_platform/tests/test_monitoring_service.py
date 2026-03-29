import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.inference_log import InferenceLog
from app.services.audit_service import AuditService
from app.services.monitoring_service import MonitoringService


class MonitoringServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
        )
        self.session_local = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        Base.metadata.create_all(bind=self.engine)

        self.db = self.session_local()
        self.audit_service = AuditService()
        self.monitoring_service = MonitoringService()

    def tearDown(self) -> None:
        self.db.close()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_summary_aggregates_inference_logs(self) -> None:
        self.audit_service.log_inference(
            self.db,
            request_source="realtime",
            request_payload={"customerID": "A"},
            model_name="model_a",
            model_version="v1",
            status="success",
            prediction=1,
            probability=0.85,
            threshold=0.31,
        )
        self.audit_service.log_inference(
            self.db,
            request_source="batch",
            request_payload={"customerID": "B"},
            model_name="model_a",
            model_version="v1",
            status="success",
            prediction=0,
            probability=0.15,
            threshold=0.31,
            job_id="job-123",
            row_index=0,
        )
        self.audit_service.log_inference(
            self.db,
            request_source="batch",
            request_payload={"customerID": "C"},
            model_name="model_a",
            model_version="v1",
            status="validation_error",
            error_message="tenure: Input should be less than or equal to 72",
            job_id="job-123",
            row_index=1,
        )
        self.audit_service.log_inference(
            self.db,
            request_source="realtime",
            request_payload={"customerID": "D"},
            model_name="model_a",
            model_version="v1",
            status="scoring_error",
            error_message="Model artifact missing",
        )

        summary = self.monitoring_service.get_summary(self.db)

        self.assertEqual(summary.total_requests, 4)
        self.assertEqual(summary.successful_predictions, 2)
        self.assertEqual(summary.average_probability, 0.5)
        self.assertEqual(summary.prediction_distribution.prediction_0, 1)
        self.assertEqual(summary.prediction_distribution.prediction_1, 1)
        self.assertEqual(summary.status_breakdown.success, 2)
        self.assertEqual(summary.status_breakdown.validation_error, 1)
        self.assertEqual(summary.status_breakdown.scoring_error, 1)
        self.assertEqual(summary.source_breakdown.realtime, 2)
        self.assertEqual(summary.source_breakdown.batch, 2)
        self.assertEqual(len(summary.daily_volume_last_7_days), 7)
        self.assertEqual(
            sum(point.request_count for point in summary.daily_volume_last_7_days),
            4,
        )

    def test_summary_handles_empty_log_table(self) -> None:
        summary = self.monitoring_service.get_summary(self.db)

        self.assertEqual(summary.total_requests, 0)
        self.assertEqual(summary.successful_predictions, 0)
        self.assertIsNone(summary.average_probability)
        self.assertEqual(summary.prediction_distribution.prediction_0, 0)
        self.assertEqual(summary.prediction_distribution.prediction_1, 0)
        self.assertEqual(summary.status_breakdown.success, 0)
        self.assertEqual(summary.status_breakdown.validation_error, 0)
        self.assertEqual(summary.status_breakdown.scoring_error, 0)
        self.assertEqual(summary.source_breakdown.realtime, 0)
        self.assertEqual(summary.source_breakdown.batch, 0)
        self.assertEqual(len(summary.daily_volume_last_7_days), 7)
        self.assertTrue(
            all(point.request_count == 0 for point in summary.daily_volume_last_7_days)
        )


if __name__ == "__main__":
    unittest.main()
