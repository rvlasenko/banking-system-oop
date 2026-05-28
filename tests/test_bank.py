import pytest

from banking_system.clients.enums import ClientStatus
from banking_system.exceptions.invalid_operation import InvalidOperationError


@pytest.fixture
def bank_with_client(bank, client, daytime):
    bank.add_client(client)
    return bank, client


class TestAuthenticateClient:
    def test_correct_pin_returns_true(self, bank_with_client):
        bank, client = bank_with_client
        assert bank.authenticate_client(client.client_id, "1234") is True

    def test_wrong_pin_returns_false(self, bank_with_client):
        bank, client = bank_with_client
        assert bank.authenticate_client(client.client_id, "0000") is False

    def test_success_resets_failed_attempts(self, bank_with_client):
        bank, client = bank_with_client
        bank.authenticate_client(client.client_id, "wrong")
        bank.authenticate_client(client.client_id, "1234")
        assert client.failed_login_attempts == 0
        assert client.is_suspicious is False

    def test_two_failures_marks_suspicious(self, bank_with_client):
        bank, client = bank_with_client
        bank.authenticate_client(client.client_id, "wrong")
        bank.authenticate_client(client.client_id, "wrong")
        assert client.is_suspicious is True

    def test_three_failures_blocks_client(self, bank_with_client):
        bank, client = bank_with_client
        for _ in range(3):
            bank.authenticate_client(client.client_id, "wrong")
        assert client.status == ClientStatus.BLOCKED

    def test_blocked_client_raises(self, bank_with_client):
        bank, client = bank_with_client
        client.status = ClientStatus.BLOCKED
        with pytest.raises(InvalidOperationError):
            bank.authenticate_client(client.client_id, "1234")

    def test_unknown_client_raises(self, bank, daytime):
        with pytest.raises(InvalidOperationError):
            bank.authenticate_client("nonexistent-id", "1234")
