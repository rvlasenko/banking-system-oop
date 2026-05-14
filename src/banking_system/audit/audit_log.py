from datetime import datetime
from pathlib import Path

from ..exceptions.invalid_operation import InvalidOperationError
from .enums import AuditLevel


class AuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def log(
        self,
        level: AuditLevel,
        message: str,
        transaction_id: str | None = None,
        client_id: str | None = None,
    ) -> None:
        if not isinstance(level, AuditLevel):
            raise InvalidOperationError("Level must be an AuditLevel")

        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "message": message,
            "transaction_id": transaction_id,
            "client_id": client_id,
        }

        self.entries.append(entry)

    def filter_by_level(self, level: AuditLevel) -> list:
        if not isinstance(level, AuditLevel):
            raise InvalidOperationError("Level must be an AuditLevel")

        return [entry for entry in self.entries if entry["level"] == level.value]

    def save_to_file(self, file_path: str | None = None) -> None:
        if file_path is None:
            project_root = Path(__file__).resolve().parents[3]
            target_path = project_root / "logs" / "audit.log"
        else:
            target_path = Path(file_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("a", encoding="utf-8") as file:
            for entry in self.entries:
                file.write(f"{entry}\n")

    def get_error_statistics(self) -> dict[str, int]:
        stats = {}

        for entry in self.entries:
            stats[entry["level"]] = stats.get(entry["level"], 0) + 1

        return stats

    def get_suspicious_entries(self) -> list[dict]:
        return [
            entry
            for entry in self.entries
            if entry["level"]
            in {
                AuditLevel.CRITICAL.value,
                AuditLevel.WARNING.value,
                AuditLevel.ERROR.value,
            }
        ]

    def get_client_risk_profile(
        self,
        client_id: str,
    ) -> dict:
        stats = {
            "info": 0,
            "warning": 0,
            "critical": 0,
            "error": 0,
        }
        client_entries = [
            entry for entry in self.entries if entry["client_id"] == client_id
        ]
        for entry in client_entries:
            level = entry["level"]
            stats[level] += 1

        return {"client_id": client_id, "total_events": len(client_entries), **stats}
