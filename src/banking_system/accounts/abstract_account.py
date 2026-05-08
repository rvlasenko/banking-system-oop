from abc import ABC, abstractmethod
from decimal import Decimal

from .enums import AccountStatus, Currency


class AbstractAccount(ABC):
    def __init__(
        self,
        owner: str,
        account_id: str,
        balance: Decimal = Decimal("0.00"),
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
    ) -> None:
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.status = status
        self.currency = currency

    @abstractmethod
    def deposit(self, amount: Decimal) -> None:
        pass

    @abstractmethod
    def withdraw(self, amount: Decimal) -> None:
        pass

    @abstractmethod
    def get_account_info(self) -> dict:
        pass
