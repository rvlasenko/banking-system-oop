from datetime import datetime
from uuid import uuid4

from ..accounts.enums import Currency
from ..exceptions.invalid_operation import InvalidOperationError
from .enums import TransactionPriority, TransactionStatus, TransactionType


class Transaction:
    def __init__(
        self,
        transaction_type: TransactionType,
        amount: int | float,
        currency: Currency,
        sender_account_id: str | None = None,
        receiver_account_id: str | None = None,
        priority: TransactionPriority = TransactionPriority.NORMAL,
        execute_after: datetime | None = None,
    ) -> None:
        self.transaction_type = self._validate_transaction_type(transaction_type)
        self.amount = self._validate_amount(amount)
        self.currency = self._validate_currency(currency)
        self.sender_account_id = self._validate_account_id(sender_account_id, "Sender")
        self.receiver_account_id = self._validate_account_id(
            receiver_account_id, "Receiver"
        )
        self.priority = self._validate_priority(priority)
        self.execute_after = self._validate_execute_after(execute_after)

        # runtime fields
        self.transaction_id = self._generate_transaction_id()
        self.status = TransactionStatus.PENDING
        self.created_at = datetime.now()
        self.processed_at: datetime | None = None
        self.failure_reason: str | None = None
        self.retry_count: int = 0
        self.fee: float = 0.0

        self._validate_account_ids_by_type()

    def __str__(self) -> str:
        return (
            f"{self.transaction_type.value.upper()} | "
            f"{self.amount} {self.currency.value} | "
            f"Status: {self.status.value} | "
            f"Fee: {self.fee}"
        )

    def get_transaction_info(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type.value,
            "amount": self.amount,
            "currency": self.currency.value,
            "sender_account_id": self.sender_account_id,
            "receiver_account_id": self.receiver_account_id,
            "priority": self.priority.value,
            "status": self.status.value,
            "fee": self.fee,
            "retry_count": self.retry_count,
            "failure_reason": self.failure_reason,
            "created_at": self.created_at.isoformat(),
            "processed_at": (
                self.processed_at.isoformat() if self.processed_at is not None else None
            ),
            "execute_after": (
                self.execute_after.isoformat()
                if self.execute_after is not None
                else None
            ),
        }

    @staticmethod
    def _generate_transaction_id() -> str:
        return f"T-{str(uuid4())[:8].upper()}"

    def _validate_transaction_type(
        self, transaction_type: TransactionType
    ) -> TransactionType:
        if not isinstance(transaction_type, TransactionType):
            raise InvalidOperationError("Transaction type must be a TransactionType")

        return transaction_type

    def _validate_amount(self, amount: int | float) -> float:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise InvalidOperationError("Amount must be a number")

        if amount <= 0:
            raise InvalidOperationError("Amount must be greater than zero")

        return float(amount)

    def _validate_currency(self, currency: Currency) -> Currency:
        if not isinstance(currency, Currency):
            raise InvalidOperationError("Currency must be a Currency")

        return currency

    def _validate_account_id(
        self, account_id: str | None, field_name: str
    ) -> str | None:
        if account_id is None:
            return None

        if not isinstance(account_id, str):
            raise InvalidOperationError(f"{field_name} must be a string")

        clean_account_id = account_id.strip()

        if not clean_account_id:
            raise InvalidOperationError(f"{field_name} cannot be empty")

        return clean_account_id

    def _validate_priority(self, priority: TransactionPriority) -> TransactionPriority:
        if not isinstance(priority, TransactionPriority):
            raise InvalidOperationError("Priority must be a TransactionPriority")

        return priority

    def _validate_execute_after(
        self, execute_after: datetime | None
    ) -> datetime | None:
        if execute_after is not None and not isinstance(execute_after, datetime):
            raise InvalidOperationError("Execute after must be a datetime")

        return execute_after

    def _validate_account_ids_by_type(self) -> None:
        if self.transaction_type == TransactionType.DEPOSIT:
            if self.receiver_account_id is None:
                raise InvalidOperationError(
                    "Deposit transaction requires receiver account"
                )

        elif self.transaction_type == TransactionType.WITHDRAW:
            if self.sender_account_id is None:
                raise InvalidOperationError(
                    "Withdraw transaction requires sender account"
                )

        elif self.transaction_type == TransactionType.TRANSFER:
            if self.sender_account_id is None or self.receiver_account_id is None:
                raise InvalidOperationError(
                    "Transfer transaction requires sender and receiver accounts"
                )
