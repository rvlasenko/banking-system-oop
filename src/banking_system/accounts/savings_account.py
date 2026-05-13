from .bank_account import BankAccount
from .enums import AccountStatus, Currency
from ..exceptions.account_exceptions import InsufficientFundsError
from ..exceptions.invalid_operation import InvalidOperationError


class SavingsAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        account_id: str | None = None,
        balance: int | float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
        min_balance: int | float = 0.0,
        monthly_interest_rate: int | float = 0.0,
    ) -> None:
        min_balance = self._validate_non_negative_number(min_balance, "Min balance")
        monthly_interest_rate = self._validate_non_negative_number(
            monthly_interest_rate,
            "Monthly interest rate",
        )

        super().__init__(
            owner=owner,
            account_id=account_id,
            balance=balance,
            status=status,
            currency=currency,
        )

        if min_balance > self._balance:
            raise InvalidOperationError("Min balance must not be greater than balance")

        self.min_balance = min_balance
        self.monthly_interest_rate = monthly_interest_rate

    def apply_monthly_interest(self) -> None:
        self._check_account_status()
        interest = self._balance * self.monthly_interest_rate / 100
        self._balance += interest

    def withdraw(self, amount: int | float) -> None:
        amount = self._validate_positive_number(amount, "Amount")
        self._check_account_status()

        if self._balance - amount < self.min_balance:
            raise InsufficientFundsError(
                "Withdrawal would violate the minimum balance requirement"
            )

        self._balance -= amount

    def get_account_info(self) -> dict:
        parent_info = super().get_account_info()

        parent_info.update(
            {
                "min_balance": self.min_balance,
                "monthly_interest_rate": self.monthly_interest_rate,
            }
        )

        return parent_info

    def __str__(self) -> str:
        return (
            f"{type(self).__name__} | "
            f"{self.owner} | "
            f"****{self.account_id[-4:]} | "
            f"{self.status.value} | "
            f"{self._balance} {self.currency.value} | "
            f"Min balance: {self.min_balance} | "
            f"Interest: {self.monthly_interest_rate}%"
        )
