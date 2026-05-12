from .bank_account import BankAccount
from .enums import AccountStatus, Currency
from ..exceptions.account_exceptions import InvalidOperationError


class PremiumAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        account_id: str | None = None,
        balance: int | float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
        overdraft_limit: int | float = 0.0,
        withdraw_limit: int | float = 10_000.0,
        fixed_fee: int | float = 0.0,
    ) -> None:
        overdraft_limit = self._validate_non_negative_number(
            overdraft_limit, "Overdraft limit"
        )
        withdraw_limit = self._validate_positive_number(
            withdraw_limit, "Withdraw limit"
        )
        fixed_fee = self._validate_non_negative_number(fixed_fee, "Fixed fee")

        super().__init__(
            owner=owner,
            account_id=account_id,
            balance=balance,
            status=status,
            currency=currency,
        )

        self.overdraft_limit = overdraft_limit
        self.withdraw_limit = withdraw_limit
        self.fixed_fee = fixed_fee

    def __str__(self) -> str:
        return (
            f"{type(self).__name__} | "
            f"{self.owner} | "
            f"****{self.account_id[-4:]} | "
            f"{self.status.value} | "
            f"{self._balance} {self.currency.value} | "
            f"Overdraft limit: {self.overdraft_limit} | "
            f"Withdraw limit: {self.withdraw_limit} | "
            f"Fixed fee: {self.fixed_fee}"
        )

    def withdraw(self, amount: int | float) -> None:
        amount = self._validate_positive_number(amount, "Amount")
        self._check_account_status()

        if amount > self.withdraw_limit:
            raise InvalidOperationError("Amount exceeds withdraw limit")

        total = amount + self.fixed_fee

        if self._balance - total < -self.overdraft_limit:
            raise InvalidOperationError("Overdraft limit exceeded")

        self._balance -= total

    def get_account_info(self) -> dict:
        parent_info = super().get_account_info()

        parent_info.update(
            {
                "overdraft_limit": self.overdraft_limit,
                "withdraw_limit": self.withdraw_limit,
                "fixed_fee": self.fixed_fee,
            }
        )

        return parent_info
