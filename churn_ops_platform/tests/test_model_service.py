import json
import shutil
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

from app.services.model_service import ModelService


class ModelServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_root = Path("tests") / "_tmp" / f"model-service-{uuid.uuid4().hex}"
        self.serving_dir = self.temp_root / "serving"
        self.challenger_dir = self.temp_root / "challenger"
        self.archive_dir = self.temp_root / "archive"
        self.promotion_log_path = self.temp_root / "model_promotions.json"
        self.env_file_path = self.temp_root / ".env"

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_root, ignore_errors=True)

    def _create_artifact(self, root: Path, artifact_id: str, *, metadata: dict | None = None) -> Path:
        artifact_dir = root / "v1" / "model_a" / artifact_id
        artifact_dir.mkdir(parents=True, exist_ok=True)
        (artifact_dir / "inference_artifact.joblib").write_text("placeholder", encoding="utf-8")
        (artifact_dir / "metadata.json").write_text(
            json.dumps(
                metadata
                or {
                    "api_version": "v1",
                    "model_name": "model_a",
                    "model_version": "v1",
                    "artifact_id": artifact_id,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return artifact_dir

    def test_list_models_returns_stage_artifacts(self) -> None:
        serving_model_dir = self.serving_dir / "v1" / "model_a"
        serving_model_dir.mkdir(parents=True, exist_ok=True)
        (serving_model_dir / "inference_artifact.joblib").write_text("placeholder", encoding="utf-8")
        (serving_model_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "api_version": "v1",
                    "model_name": "model_a",
                    "model_version": "v1",
                    "artifact_id": "artifact_serving",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        self._create_artifact(self.challenger_dir, "artifact_challenger")
        self._create_artifact(self.archive_dir, "artifact_archive")

        service = ModelService()

        with patch("app.services.model_service.settings.serving_dir", self.serving_dir), patch(
            "app.services.model_service.settings.challenger_dir",
            self.challenger_dir,
        ), patch(
            "app.services.model_service.settings.archive_dir",
            self.archive_dir,
        ), patch(
            "app.services.model_service.settings.api_version",
            "v1",
        ), patch(
            "app.services.model_service.settings.active_model_name",
            "model_a",
        ), patch(
            "app.services.model_service.settings.active_model_version",
            "v1",
        ):
            result = service.list_models(promotion_log_path=self.promotion_log_path)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].model_name, "model_a")
        self.assertEqual(result[0].active_api_version, "v1")
        self.assertEqual([artifact.stage for artifact in result[0].artifacts], ["serving", "challenger", "archive"])
        self.assertEqual(result[0].artifacts[0].artifact_id, "artifact_serving")
        self.assertTrue(result[0].artifacts[0].is_active)

    def test_promote_model_archives_current_serving_and_persists_env(self) -> None:
        serving_model_dir = self.serving_dir / "v1" / "model_a"
        serving_model_dir.mkdir(parents=True, exist_ok=True)
        (serving_model_dir / "inference_artifact.joblib").write_text("current-serving", encoding="utf-8")
        (serving_model_dir / "metadata.json").write_text(
            json.dumps(
                {
                    "api_version": "v1",
                    "model_name": "model_a",
                    "model_version": "v1",
                    "artifact_id": "artifact_old",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        challenger_dir = self._create_artifact(self.challenger_dir, "artifact_new")
        (challenger_dir / "inference_artifact.joblib").write_text("new-serving", encoding="utf-8")
        self.env_file_path.write_text(
            "ACTIVE_MODEL_NAME=model_a\nACTIVE_MODEL_VERSION=v1\n",
            encoding="utf-8",
        )

        service = ModelService()

        with patch("app.services.model_service.settings.serving_dir", self.serving_dir), patch(
            "app.services.model_service.settings.challenger_dir",
            self.challenger_dir,
        ), patch(
            "app.services.model_service.settings.archive_dir",
            self.archive_dir,
        ), patch(
            "app.services.model_service.settings.api_version",
            "v1",
        ), patch(
            "app.services.model_service.settings.active_model_name",
            "model_a",
        ), patch(
            "app.services.model_service.settings.active_model_version",
            "v1",
        ):
            result = service.promote_model(
                "model_a",
                "artifact_new",
                env_file_path=self.env_file_path,
                promotion_log_path=self.promotion_log_path,
            )

        self.assertEqual(result.artifact_id, "artifact_new")
        self.assertTrue((self.archive_dir / "v1" / "model_a" / "artifact_old" / "inference_artifact.joblib").exists())
        self.assertEqual(
            (self.serving_dir / "v1" / "model_a" / "inference_artifact.joblib").read_text(encoding="utf-8"),
            "new-serving",
        )
        self.assertEqual(self.env_file_path.read_text(encoding="utf-8").splitlines(), [
            "ACTIVE_MODEL_NAME=model_a",
            "ACTIVE_MODEL_VERSION=v1",
        ])
        history = json.loads(self.promotion_log_path.read_text(encoding="utf-8"))
        self.assertEqual(history[-1]["artifact_id"], "artifact_new")

    def test_promote_model_raises_for_missing_challenger_artifact(self) -> None:
        service = ModelService()

        with patch("app.services.model_service.settings.challenger_dir", self.challenger_dir), patch(
            "app.services.model_service.settings.api_version",
            "v1",
        ):
            with self.assertRaises(HTTPException) as ctx:
                service.promote_model("model_a", "artifact_missing")

        self.assertEqual(ctx.exception.status_code, 404)
        self.assertEqual(ctx.exception.detail, "Challenger artifact not found.")

    def test_list_models_includes_last_promotion_timestamp(self) -> None:
        self._create_artifact(self.challenger_dir, "artifact_candidate")
        self.promotion_log_path.write_text(
            json.dumps(
                [
                    {
                        "api_version": "v1",
                        "model_name": "model_a",
                        "artifact_id": "artifact_candidate",
                        "promoted_at": "2026-03-29T12:00:00+00:00",
                    }
                ],
                indent=2,
            ),
            encoding="utf-8",
        )

        service = ModelService()

        with patch("app.services.model_service.settings.serving_dir", self.serving_dir), patch(
            "app.services.model_service.settings.challenger_dir",
            self.challenger_dir,
        ), patch(
            "app.services.model_service.settings.archive_dir",
            self.archive_dir,
        ), patch(
            "app.services.model_service.settings.api_version",
            "v1",
        ), patch(
            "app.services.model_service.settings.active_model_name",
            "model_a",
        ), patch(
            "app.services.model_service.settings.active_model_version",
            "v1",
        ):
            result = service.list_models(promotion_log_path=self.promotion_log_path)

        challenger = next(artifact for artifact in result[0].artifacts if artifact.stage == "challenger")
        self.assertEqual(challenger.last_promoted_at, "2026-03-29T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
