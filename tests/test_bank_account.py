import pytest

from banking_system.accounts.bank_account import BankAccount
from banking_system.accounts.enums import AccountStatus, Currency
from banking_system.exceptions.account_exceptions import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
)
from banking_system.exceptions.invalid_operation import InvalidOperationError


class TestDeposit:
    def test_increases_balance(self, account):
        account.deposit(500)
        assert account._balance == 1500.0

    def test_raises_on_frozen_account(self, account):
        account.status = AccountStatus.FROZEN
        with pytest.raises(AccountFrozenError):
            account.deposit(100)

    def test_raises_on_closed_account(self, account):
        account.status = AccountStatus.CLOSED
        with pytest.raises(AccountClosedError):
            account.deposit(100)

    def test_raises_on_zero_amount(self, account):
        with pytest.raises(InvalidOperationError):
            account.deposit(0)

    def test_raises_on_negative_amount(self, account):
        with pytest.raises(InvalidOperationError):
            account.deposit(-100)


class TestWithdraw:
    def test_decreases_balance(self, account):
        account.withdraw(400)
        assert account._balance == 600.0

    def test_raises_insufficient_funds(self, account):
        with pytest.raises(InsufficientFundsError):
            account.withdraw(9999)

    def test_raises_on_frozen_account(self, account):
        account.status = AccountStatus.FROZEN
        with pytest.raises(AccountFrozenError):
            account.withdraw(100)

    def test_raises_on_closed_account(self, account):
        account.status = AccountStatus.CLOSED
        with pytest.raises(AccountClosedError):
            account.withdraw(100)

    def test_exact_balance_succeeds(self, account):
        account.withdraw(1000.0)
        assert account._balance == 0.0


class TestValidation:
    def test_empty_owner_raises(self):
        with pytest.raises(InvalidOperationError):
            BankAccount(owner="")

    def test_whitespace_owner_raises(self):
        with pytest.raises(InvalidOperationError):
            BankAccount(owner="   ")

    def test_negative_balance_raises(self):
        with pytest.raises(InvalidOperationError):
            BankAccount(owner="Alice", balance=-1)

    def test_zero_balance_is_valid(self):
        acc = BankAccount(owner="Alice", balance=0)
        assert acc._balance == 0.0

    def test_invalid_currency_type_raises(self):
        with pytest.raises(InvalidOperationError):
            BankAccount(owner="Alice", currency="USD")

    def test_invalid_status_type_raises(self):
        with pytest.raises(InvalidOperationError):
            BankAccount(owner="Alice", status="active")
