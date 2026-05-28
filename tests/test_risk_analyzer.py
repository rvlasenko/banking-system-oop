from datetime import datetime

import pytest

from banking_system.accounts.enums import Currency
from banking_system.audit.enums import RiskLevel
from banking_system.transactions.enums import TransactionType
from banking_system.transactions.transaction import Transaction

DAYTIME = datetime(2024, 1, 1, 10, 0, 0)
NIGHTTIME = datetime(2024, 1, 1, 3, 0, 0)


def make_deposit(amount: float, receiver_id: str = "ACC-RECV") -> Transaction:
    t = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=amount,
        currency=Currency.USD,
        receiver_account_id=receiver_id,
    )
    t.created_at = DAYTIME
    return t


def make_withdraw(amount: float, sender_id: str = "ACC-SENDER") -> Transaction:
    t = Transaction(
        transaction_type=TransactionType.WITHDRAW,
        amount=amount,
        currency=Currency.USD,
        sender_account_id=sender_id,
    )
    t.created_at = DAYTIME
    return t


def make_transfer(
    amount: float,
    sender_id: str = "ACC-SENDER",
    receiver_id: str = "ACC-RECV",
) -> Transaction:
    t = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=amount,
        currency=Currency.USD,
        sender_account_id=sender_id,
        receiver_account_id=receiver_id,
    )
    t.created_at = DAYTIME
    return t


class TestAmountThresholds:
    def test_amount_at_high_threshold_returns_high(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_deposit(10_000)) == RiskLevel.HIGH

    def test_amount_above_high_threshold_returns_high(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_deposit(50_000)) == RiskLevel.HIGH

    def test_amount_at_medium_threshold_returns_medium(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_deposit(5_000)) == RiskLevel.MEDIUM

    def test_amount_below_medium_threshold_returns_low(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_deposit(100)) == RiskLevel.LOW


class TestNightTransaction:
    def test_night_hour_returns_medium(self, risk_analyzer):
        txn = make_deposit(100)
        txn.created_at = NIGHTTIME
        assert risk_analyzer.analyze_transaction(txn) == RiskLevel.MEDIUM

    def test_midnight_returns_medium(self, risk_analyzer):
        txn = make_deposit(100)
        txn.created_at = datetime(2024, 1, 1, 0, 0, 0)
        assert risk_analyzer.analyze_transaction(txn) == RiskLevel.MEDIUM

    def test_hour_5_is_outside_window(self, risk_analyzer):
        txn = make_deposit(100)
        txn.created_at = datetime(2024, 1, 1, 5, 0, 0)
        assert risk_analyzer.analyze_transaction(txn) == RiskLevel.LOW

    def test_daytime_returns_low(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_deposit(100)) == RiskLevel.LOW


class TestFrequentTransactions:
    def test_five_withdrawals_in_one_minute_triggers_medium(self, risk_analyzer):
        for _ in range(5):
            risk_analyzer.analyze_transaction(make_withdraw(100))

        sixth = make_withdraw(100)
        assert risk_analyzer.analyze_transaction(sixth) == RiskLevel.MEDIUM

    def test_four_withdrawals_do_not_trigger(self, risk_analyzer):
        for _ in range(4):
            risk_analyzer.analyze_transaction(make_withdraw(100))

        fifth = make_withdraw(100)
        assert risk_analyzer.analyze_transaction(fifth) == RiskLevel.LOW


class TestNewReceiver:
    def test_first_transfer_to_unknown_receiver_returns_medium(self, risk_analyzer):
        assert risk_analyzer.analyze_transaction(make_transfer(100)) == RiskLevel.MEDIUM

    def test_second_transfer_to_known_receiver_returns_low(self, risk_analyzer):
        risk_analyzer.analyze_transaction(make_transfer(100))
        assert risk_analyzer.analyze_transaction(make_transfer(100)) == RiskLevel.LOW

    def test_deposit_to_new_account_is_not_flagged(self, risk_analyzer):
        # deposits have no sender, new receiver logic only applies to transfers
        assert risk_analyzer.analyze_transaction(make_deposit(100)) == RiskLevel.LOW
