from .bank_account import BankAccount
from .enums import AccountStatus, Currency
from ..exceptions.account_exceptions import (
    InsufficientFundsError,
    InvalidOperationError,
)


class InvestmentAccount(BankAccount):
    def __init__(
        self,
        owner: str,
        account_id: str | None = None,
        balance: int | float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
        portfolio: dict[str, int | float] | None = None,
    ) -> None:
        super().__init__(
            owner=owner,
            account_id=account_id,
            balance=balance,
            status=status,
            currency=currency,
        )

        self.portfolio = self._validate_portfolio(portfolio)

    def __str__(self) -> str:
        portfolio_value = sum(self.portfolio.values())

        return (
            f"{type(self).__name__} | "
            f"{self.owner} | "
            f"****{self.account_id[-4:]} | "
            f"{self.status.value} | "
            f"{self._balance} {self.currency.value} | "
            f"Portfolio value: {portfolio_value}"
        )

    def project_yearly_growth(self) -> dict[str, float]:
        growth_rates = {
            "stocks": 0.08,
            "bonds": 0.03,
            "etf": 0.06,
        }

        projected_portfolio = {}

        for key, value in self.portfolio.items():
            rate = growth_rates.get(key, 0)
            projected_portfolio[key] = value * (1 + rate)

        return projected_portfolio

    def withdraw(self, amount: int | float) -> None:
        amount = self._validate_positive_number(amount, "Amount")
        self._check_account_status()

        if amount > self._balance:
            raise InsufficientFundsError("Insufficient funds for this withdrawal")

        self._balance -= amount

    def get_account_info(self) -> dict:
        parent_info = super().get_account_info()

        parent_info.update(
            {
                "portfolio": self.portfolio,
            }
        )

        return parent_info

    def _validate_portfolio(
        self, portfolio: dict[str, int | float] | None
    ) -> dict[str, int | float]:
        allowed_assets = {"stocks", "bonds", "etf"}
        validated_portfolio = {}

        if portfolio is None:
            return validated_portfolio

        for key, value in portfolio.items():
            if key not in allowed_assets:
                raise InvalidOperationError(f"Unsupported asset type: {key}")

            validated_value = self._validate_non_negative_number(value, key)

            validated_portfolio[key] = validated_value

        return validated_portfolio
