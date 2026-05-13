from datetime import datetime

from ..clients.client import Client
from ..clients.enums import ClientStatus
from ..accounts.enums import AccountStatus
from ..accounts.bank_account import BankAccount
from ..exceptions.invalid_operation import InvalidOperationError


class Bank:
    def __init__(self):
        self.clients: dict[str, Client] = {}
        self.accounts: dict[str, BankAccount] = {}

    def add_client(self, client: Client) -> None:
        if not isinstance(client, Client):
            raise InvalidOperationError("Client must be an instance of Client")

        if client.client_id in self.clients:
            raise InvalidOperationError("Client already exists")

        self.clients[client.client_id] = client

    def open_account(self, client_id: str, account: BankAccount) -> None:
        self._ensure_operations_allowed()

        if not isinstance(account, BankAccount):
            raise InvalidOperationError("Account must be an instance of BankAccount")

        if client_id not in self.clients:
            raise InvalidOperationError("Client doesn't exist")

        client = self.clients[client_id]

        if client.status is not ClientStatus.ACTIVE:
            raise InvalidOperationError("Client must be active")

        if account.account_id in self.accounts:
            raise InvalidOperationError("Account already exists")

        self.accounts[account.account_id] = account
        client.account_ids.append(account.account_id)

    def close_account(self, account_id: str) -> None:
        self._ensure_operations_allowed()
        self._change_account_status(account_id, AccountStatus.CLOSED)

    def freeze_account(self, account_id: str) -> None:
        self._ensure_operations_allowed()
        self._change_account_status(account_id, AccountStatus.FROZEN)

    def unfreeze_account(self, account_id: str) -> None:
        self._ensure_operations_allowed()
        account = self._get_account(account_id)

        if account.status == AccountStatus.CLOSED:
            raise InvalidOperationError("Closed account cannot be unfrozen")

        self._change_account_status(account_id, AccountStatus.ACTIVE)

    def authenticate_client(self, client_id: str, pin_code: str) -> bool:
        self._ensure_operations_allowed()

        if client_id not in self.clients:
            raise InvalidOperationError("Client doesn't exist")

        client = self.clients[client_id]

        if client.status is ClientStatus.BLOCKED:
            raise InvalidOperationError("Client is blocked")

        if pin_code != client.pin_code:
            client.failed_login_attempts += 1

            if client.failed_login_attempts >= 2:
                client.is_suspicious = True

            if client.failed_login_attempts >= 3:
                client.status = ClientStatus.BLOCKED
                return False

        else:
            client.failed_login_attempts = 0
            client.is_suspicious = False
            return True

        return False

    def search_accounts(
        self,
        client_id: str | None = None,
        status: AccountStatus | None = None,
    ) -> list[BankAccount]:
        accounts = list(self.accounts.values())

        if client_id is not None:
            if client_id not in self.clients:
                raise InvalidOperationError("Client doesn't exist")

            client = self.clients[client_id]
            accounts = [
                account
                for account in accounts
                if account.account_id in client.account_ids
            ]

        if status is not None:
            accounts = [account for account in accounts if account.status == status]

        return accounts

    def get_total_balance(self) -> float:
        return sum(account._balance for account in self.accounts.values())

    def get_clients_ranking(self) -> list[tuple[str, float]]:
        clients = {}

        for client in self.clients.values():
            total_balance = 0

            for account_id in client.account_ids:
                account = self._get_account(account_id)
                total_balance += account._balance

            clients[client.full_name] = total_balance

        return sorted(
            clients.items(),
            key=lambda item: item[1],
            reverse=True,
        )

    def _ensure_operations_allowed(self) -> None:
        if self._is_night_time():
            raise InvalidOperationError("Bank operations are not allowed at night")

    def _is_night_time(self) -> bool:
        current_hour = datetime.now().hour
        return current_hour >= 0 and current_hour < 5

    def _get_account(self, account_id: str) -> BankAccount:
        if account_id not in self.accounts:
            raise InvalidOperationError("Account doesn't exist")

        return self.accounts[account_id]

    def _change_account_status(self, account_id: str, status: AccountStatus) -> None:
        account = self._get_account(account_id)
        account.status = status
