from abc import ABC, abstractmethod

from .enums import AccountStatus, Currency


class AbstractAccount(ABC):
    def __init__(
        self,
        owner: str,
        account_id: str,
        balance: int | float = 0.0,
        status: AccountStatus = AccountStatus.ACTIVE,
        currency: Currency = Currency.USD,
    ) -> None:
        self.account_id = account_id
        self.owner = owner
        self._balance = balance
        self.status = status
        self.currency = currency

    @abstractmethod
    def deposit(self, amount: int | float) -> None:
        pass

    @abstractmethod
    def withdraw(self, amount: int | float) -> None:
        pass

    @abstractmethod
    def get_account_info(self) -> dict:
        pass
