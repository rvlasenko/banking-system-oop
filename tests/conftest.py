import pytest
from unittest.mock import MagicMock

from banking_system.accounts.bank_account import BankAccount
from banking_system.audit.audit_log import AuditLog
from banking_system.audit.risk_analyzer import RiskAnalyzer
from banking_system.bank.bank import Bank
from banking_system.clients.client import Client
from banking_system.transactions.transaction_processor import TransactionProcessor


@pytest.fixture
def daytime(monkeypatch):
    """Patch datetime.now() in bank.py to a daytime hour so operations are allowed."""
    mock_dt = MagicMock()
    mock_dt.now.return_value.hour = 10
    monkeypatch.setattr("banking_system.bank.bank.datetime", mock_dt)


@pytest.fixture
def account():
    return BankAccount(owner="Alice", balance=1000.0)


@pytest.fixture
def client():
    return Client(full_name="Alice Smith", age=30, pin_code="1234")


@pytest.fixture
def bank():
    return Bank()


@pytest.fixture
def audit_log():
    return AuditLog()


@pytest.fixture
def risk_analyzer():
    return RiskAnalyzer()


@pytest.fixture
def processor(bank, audit_log, risk_analyzer):
    return TransactionProcessor(bank=bank, audit_log=audit_log, risk_analyzer=risk_analyzer)
