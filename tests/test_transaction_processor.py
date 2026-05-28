import pytest

from banking_system.accounts.bank_account import BankAccount
from banking_system.accounts.enums import Currency
from banking_system.audit.enums import AuditLevel
from banking_system.exceptions.invalid_operation import InvalidOperationError
from banking_system.transactions.enums import TransactionStatus, TransactionType
from banking_system.transactions.transaction import Transaction


def make_deposit(amount: float, receiver_id: str = "ACC-001") -> Transaction:
    return Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        currency=Currency.USD,
        receiver_account_id=receiver_id,
    )


class TestCalculateFee:
    def test_transfer_fee_is_one_percent(self, processor):
        txn = Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=1000,
            currency=Currency.USD,
            sender_account_id="S",
            receiver_account_id="R",
        )
        assert processor._calculate_fee(txn) == pytest.approx(10.0)

    def test_deposit_has_no_fee(self, processor):
        assert processor._calculate_fee(make_deposit(1000)) == 0.0

    def test_withdraw_has_no_fee(self, processor):
        txn = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=1000,
            currency=Currency.USD,
            sender_account_id="S",
        )
        assert processor._calculate_fee(txn) == 0.0


class TestConvertAmount:
    def test_same_currency_returns_original_amount(self, processor):
        assert processor._convert_amount(100, Currency.USD, Currency.USD) == 100

    def test_usd_to_eur(self, processor):
        assert processor._convert_amount(100, Currency.USD, Currency.EUR) == pytest.approx(92.0)

    def test_unsupported_pair_raises(self, processor):
        with pytest.raises(InvalidOperationError):
            processor._convert_amount(100, Currency.KZT, Currency.EUR)


class TestHighRiskBlocking:
    def test_transaction_status_is_failed(self, processor):
        txn = make_deposit(15_000)
        processor.process_transaction(txn)
        assert txn.status == TransactionStatus.FAILED

    def test_failure_reason_mentions_risk_analyzer(self, processor):
        txn = make_deposit(15_000)
        processor.process_transaction(txn)
        assert "risk analyzer" in txn.failure_reason.lower()

    def test_high_risk_is_logged_as_critical(self, processor, audit_log):
        txn = make_deposit(15_000)
        processor.process_transaction(txn)
        entries = audit_log.filter_by_level(AuditLevel.CRITICAL)
        assert len(entries) == 1


class TestMediumRiskWarning:
    def test_medium_risk_logs_warning_and_completes(self, processor, bank, audit_log):
        account = BankAccount(owner="Bob", balance=0)
        bank.accounts[account.account_id] = account

        txn = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=7_000,
            currency=Currency.USD,
            receiver_account_id=account.account_id,
        )
        processor.process_transaction(txn)

        assert txn.status == TransactionStatus.COMPLETED
        assert len(audit_log.filter_by_level(AuditLevel.WARNING)) == 1
