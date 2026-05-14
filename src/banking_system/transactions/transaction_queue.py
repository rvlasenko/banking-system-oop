from datetime import datetime

from ..exceptions.invalid_operation import InvalidOperationError
from .enums import TransactionStatus
from .transaction import Transaction


class TransactionQueue:
    def __init__(self) -> None:
        self.transactions: list[Transaction] = []

    def add_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Transaction must be an instance of Transaction"
            )

        if transaction.status is not TransactionStatus.PENDING:
            raise InvalidOperationError("Transaction status must be pending")

        if any(
            trans.transaction_id == transaction.transaction_id
            for trans in self.transactions
        ):
            raise InvalidOperationError("Transaction already exists in queue")

        self.transactions.append(transaction)

    def cancel_transaction(self, transaction_id: str) -> None:
        transaction = self._get_transaction(transaction_id)

        transaction.status = TransactionStatus.CANCELLED

        self.transactions.remove(transaction)

    def remove_transaction(self, transaction_id: str) -> None:
        transaction = self._get_transaction(transaction_id)

        self.transactions.remove(transaction)

    def get_ready_transactions(self) -> list[Transaction]:
        current_time = datetime.now()

        return [
            transaction
            for transaction in self.transactions
            if transaction.status is TransactionStatus.PENDING
            and (
                transaction.execute_after is None
                or transaction.execute_after <= current_time
            )
        ]

    def get_next_transaction(self) -> Transaction | None:
        ready_transactions = self.get_ready_transactions()

        if not ready_transactions:
            return None

        return sorted(
            ready_transactions,
            key=lambda transaction: transaction.priority.value,
            reverse=True,
        )[0]

    def _get_transaction(self, transaction_id: str) -> Transaction:
        for transaction in self.transactions:
            if transaction.transaction_id == transaction_id:
                return transaction

        raise InvalidOperationError("Transaction doesn't exist in queue")
