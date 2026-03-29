import json
import shutil
from pathlib import Path
from typing import Any


class ModelRepository:
    def list_model_names(self, *roots: Path) -> list[str]:
        model_names: set[str] = set()

        for root in roots:
            if not root.exists():
                continue

            for api_dir in root.iterdir():
                if not api_dir.is_dir():
                    continue
                for model_dir in api_dir.iterdir():
                    if model_dir.is_dir():
                        model_names.add(model_dir.name)

        return sorted(model_names)

    def list_artifact_directories(
        self,
        *,
        root: Path,
        api_version: str,
        model_name: str,
    ) -> list[Path]:
        model_root = root / api_version / model_name
        if not model_root.exists():
            return []

        return sorted(
            [path for path in model_root.iterdir() if path.is_dir()],
            key=lambda path: path.name,
        )

    def read_promotion_history(self, promotion_log_path: Path) -> list[dict[str, Any]]:
        if not promotion_log_path.exists():
            return []

        content = promotion_log_path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        return json.loads(content)

    def append_promotion_event(
        self,
        promotion_log_path: Path,
        *,
        api_version: str,
        model_name: str,
        artifact_id: str,
        promoted_at: str,
    ) -> None:
        events = self.read_promotion_history(promotion_log_path)
        events.append(
            {
                "api_version": api_version,
                "model_name": model_name,
                "artifact_id": artifact_id,
                "promoted_at": promoted_at,
            }
        )
        promotion_log_path.write_text(json.dumps(events, indent=2), encoding="utf-8")

    def persist_active_model(
        self,
        env_file_path: Path,
        *,
        model_name: str,
        model_version: str,
    ) -> None:
        lines: list[str] = []
        if env_file_path.exists():
            lines = env_file_path.read_text(encoding="utf-8").splitlines()

        updated_lines: list[str] = []
        seen_name = False
        seen_version = False

        for line in lines:
            if line.startswith("ACTIVE_MODEL_NAME="):
                updated_lines.append(f"ACTIVE_MODEL_NAME={model_name}")
                seen_name = True
            elif line.startswith("ACTIVE_MODEL_VERSION="):
                updated_lines.append(f"ACTIVE_MODEL_VERSION={model_version}")
                seen_version = True
            else:
                updated_lines.append(line)

        if not seen_name:
            updated_lines.append(f"ACTIVE_MODEL_NAME={model_name}")
        if not seen_version:
            updated_lines.append(f"ACTIVE_MODEL_VERSION={model_version}")

        env_file_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")

    def artifact_exists(
        self,
        *,
        root: Path,
        api_version: str,
        model_name: str,
        artifact_id: str,
    ) -> bool:
        return (root / api_version / model_name / artifact_id / "inference_artifact.joblib").exists()

    def copy_tree(self, source_dir: Path, target_dir: Path) -> None:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        shutil.copytree(source_dir, target_dir)

    def copy_file(self, source_path: Path, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

    def read_metadata(self, metadata_path: Path) -> dict[str, Any]:
        if not metadata_path.exists():
            return {}
        return json.loads(metadata_path.read_text(encoding="utf-8-sig"))

    def write_metadata(self, metadata_path: Path, metadata: dict[str, Any]) -> None:
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
