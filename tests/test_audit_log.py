import pytest

from banking_system.audit.audit_log import AuditLog
from banking_system.audit.enums import AuditLevel
from banking_system.exceptions.invalid_operation import InvalidOperationError


@pytest.fixture
def populated_log():
    log = AuditLog()
    log.log(AuditLevel.INFO, "deposit completed", transaction_id="T1", client_id="C1")
    log.log(AuditLevel.WARNING, "medium risk", transaction_id="T2", client_id="C1")
    log.log(AuditLevel.ERROR, "insufficient funds", transaction_id="T3", client_id="C2")
    log.log(AuditLevel.CRITICAL, "blocked by risk", transaction_id="T4", client_id="C1")
    return log


class TestFilterByLevel:
    def test_returns_only_matching_entries(self, populated_log):
        entries = populated_log.filter_by_level(AuditLevel.INFO)
        assert len(entries) == 1
        assert entries[0]["message"] == "deposit completed"

    def test_returns_empty_when_no_match(self):
        log = AuditLog()
        log.log(AuditLevel.INFO, "ok")
        assert log.filter_by_level(AuditLevel.ERROR) == []

    def test_invalid_level_type_raises(self, audit_log):
        with pytest.raises(InvalidOperationError):
            audit_log.filter_by_level("INFO")


class TestErrorStatistics:
    def test_counts_each_level(self, populated_log):
        stats = populated_log.get_error_statistics()
        assert stats["info"] == 1
        assert stats["warning"] == 1
        assert stats["error"] == 1
        assert stats["critical"] == 1

    def test_empty_log_returns_empty_dict(self):
        assert AuditLog().get_error_statistics() == {}


class TestSuspiciousEntries:
    def test_includes_warning_error_critical(self, populated_log):
        entries = populated_log.get_suspicious_entries()
        levels = {e["level"] for e in entries}
        assert levels == {"warning", "error", "critical"}

    def test_excludes_info(self, populated_log):
        entries = populated_log.get_suspicious_entries()
        assert all(e["level"] != "info" for e in entries)


class TestClientRiskProfile:
    def test_counts_events_for_client(self, populated_log):
        profile = populated_log.get_client_risk_profile("C1")
        assert profile["total_events"] == 3
        assert profile["info"] == 1
        assert profile["warning"] == 1
        assert profile["critical"] == 1
        assert profile["error"] == 0

    def test_unknown_client_returns_all_zeros(self, populated_log):
        profile = populated_log.get_client_risk_profile("UNKNOWN")
        assert profile["total_events"] == 0
        assert profile["info"] == 0


class TestSaveToFile:
    def test_creates_file_with_log_content(self, tmp_path):
        log = AuditLog()
        log.log(AuditLevel.INFO, "test entry")
        target = tmp_path / "audit.log"
        log.save_to_file(str(target))
        assert target.exists()
        assert "test entry" in target.read_text()
