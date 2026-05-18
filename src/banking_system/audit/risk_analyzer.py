from datetime import timedelta

from ..transactions.enums import TransactionType
from .enums import RiskLevel
from ..transactions.transaction import Transaction
from ..exceptions.invalid_operation import InvalidOperationError


class RiskAnalyzer:
    def __init__(self) -> None:
        self.transaction_history: dict[str, list[Transaction]] = {}
        self.known_receivers: dict[str, set[str]] = {}

    def analyze_transaction(self, transaction: Transaction) -> RiskLevel:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Transaction must be an instance of Transaction"
            )

        risk_level = RiskLevel.LOW

        if transaction.amount >= 10_000:
            risk_level = RiskLevel.HIGH

        elif transaction.amount >= 5000:
            risk_level = RiskLevel.MEDIUM

        elif self._is_night_transaction(transaction):
            risk_level = RiskLevel.MEDIUM

        elif self._is_frequent_transactions(transaction):
            risk_level = RiskLevel.MEDIUM

        elif self._is_new_receiver(transaction):
            risk_level = RiskLevel.MEDIUM

        self._save_transaction(transaction)
        self._save_receiver(transaction)

        return risk_level

    def _save_transaction(self, transaction: Transaction) -> None:
        if transaction.sender_account_id is None:
            return

        history = self.transaction_history.setdefault(transaction.sender_account_id, [])

        history.append(transaction)

    def _is_night_transaction(self, transaction: Transaction) -> bool:
        transaction_hour = transaction.created_at.hour
        return transaction_hour >= 0 and transaction_hour < 5

    def _is_frequent_transactions(
        self,
        transaction: Transaction,
    ) -> bool:
        if transaction.sender_account_id is None:
            return False

        history = self.transaction_history.get(transaction.sender_account_id, [])

        recent_transactions = [
            trans
            for trans in history
            if timedelta(0)
            <= transaction.created_at - trans.created_at
            <= timedelta(minutes=1)
        ]

        return len(recent_transactions) >= 5

    def _save_receiver(self, transaction: Transaction) -> None:
        if transaction.sender_account_id is None:
            return

        if transaction.receiver_account_id is None:
            return

        receivers = self.known_receivers.setdefault(
            transaction.sender_account_id,
            set(),
        )

        receivers.add(transaction.receiver_account_id)

    def _is_new_receiver(self, transaction: Transaction) -> bool:
        if transaction.transaction_type != TransactionType.TRANSFER:
            return False

        if transaction.sender_account_id is None:
            return False

        if transaction.receiver_account_id is None:
            return False

        sender_receivers = self.known_receivers.get(
            transaction.sender_account_id,
            set(),
        )

        return transaction.receiver_account_id not in sender_receivers
