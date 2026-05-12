from uuid import uuid4

from .abstract_account import AbstractAccount
from .enums import AccountStatus, Currency
from ..exceptions.account_exceptions import (
    InvalidOperationError,
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
)


class BankAccount(AbstractAccount):
    def __init__(
        self,
        owner: str,
        account_id: str | None = None,
        balance: int | float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
    ) -> None:
        owner = self._validate_owner(owner)
        account_id = self._validate_account_id(account_id)
        balance = self._validate_non_negative_number(balance, "Balance")
        status = self._validate_status(status)
        currency = self._validate_currency(currency)

        super().__init__(
            owner=owner,
            account_id=account_id,
            balance=balance,
            status=status,
            currency=currency,
        )

    def __str__(self) -> str:
        return (
            f"{type(self).__name__} | "
            f"{self.owner} | "
            f"****{self.account_id[-4:]} | "
            f"{self.status.value} | "
            f"{self._balance} {self.currency.value}"
        )

    def deposit(self, amount: int | float) -> None:
        amount = self._validate_positive_number(amount, "Amount")
        self._check_account_status()
        self._balance += amount

    def withdraw(self, amount: int | float) -> None:
        amount = self._validate_positive_number(amount, "Amount")
        self._check_account_status()

        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds for this withdrawal")

        self._balance -= amount

    def get_account_info(self) -> dict:
        return {
            "account_type": type(self).__name__,
            "owner": self.owner,
            "account_id": self.account_id,
            "balance": self._balance,
            "status": self.status.value,
            "currency": self.currency.value,
        }

    def _validate_owner(self, owner: str) -> str:
        if not isinstance(owner, str):
            raise InvalidOperationError("Owner must be a string")

        clean_owner = owner.strip()

        if not clean_owner:
            raise InvalidOperationError("Owner cannot be empty")

        return clean_owner

    @staticmethod
    def _generate_account_id() -> str:
        return str(uuid4())[:8].upper()

    def _validate_account_id(self, account_id: str | None) -> str:
        if account_id is None:
            # Generate short random account ID if not provided
            return self._generate_account_id()
        elif not isinstance(account_id, str):
            raise InvalidOperationError("Account ID must be a string")

        clean_account_id = account_id.strip()

        if not clean_account_id:
            raise InvalidOperationError("Account ID cannot be empty")

        return clean_account_id

    def _to_float(self, value: int | float, field_name: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise InvalidOperationError(f"{field_name} must be a number")

        return float(value)

    def _validate_non_negative_number(
        self,
        value: int | float,
        field_name: str,
    ) -> float:
        normalized_value = self._to_float(value, field_name)

        if normalized_value < 0:
            raise InvalidOperationError(
                f"{field_name} must be greater than or equal to zero"
            )

        return normalized_value

    def _validate_positive_number(
        self,
        value: int | float,
        field_name: str,
    ) -> float:
        normalized_value = self._to_float(value, field_name)

        if normalized_value <= 0:
            raise InvalidOperationError(f"{field_name} must be greater than zero")

        return normalized_value

    @staticmethod
    def _validate_status(status: AccountStatus) -> AccountStatus:
        if not isinstance(status, AccountStatus):
            raise InvalidOperationError("Status must be an AccountStatus")

        return status

    @staticmethod
    def _validate_currency(currency: Currency) -> Currency:
        if not isinstance(currency, Currency):
            raise InvalidOperationError("Currency must be a Currency")

        return currency

    def _check_account_status(self) -> None:
        if self.status == AccountStatus.FROZEN:
            raise AccountFrozenError("Your account is frozen")

        if self.status == AccountStatus.CLOSED:
            raise AccountClosedError("Your account is closed")
