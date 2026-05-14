from datetime import datetime

from ..accounts.bank_account import BankAccount
from ..bank.bank import Bank
from ..exceptions.account_exceptions import (
    AccountClosedError,
    AccountFrozenError,
    InsufficientFundsError,
)
from ..exceptions.invalid_operation import InvalidOperationError
from .enums import TransactionStatus, TransactionType
from .transaction import Transaction
from .transaction_queue import TransactionQueue


class TransactionProcessor:
    def __init__(self, bank: Bank) -> None:
        if not isinstance(bank, Bank):
            raise InvalidOperationError("Bank must be an instance of Bank")

        self.bank = bank

    def process_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Transaction must be an instance of Transaction"
            )

        if transaction.status != TransactionStatus.PENDING:
            raise InvalidOperationError("Only pending transactions can be processed")

        transaction.status = TransactionStatus.PROCESSING
        transaction.fee = self._calculate_fee(transaction)

        try:
            if transaction.transaction_type == TransactionType.DEPOSIT:
                self._process_deposit(transaction)

            elif transaction.transaction_type == TransactionType.WITHDRAW:
                self._process_withdraw(transaction)

            elif transaction.transaction_type == TransactionType.TRANSFER:
                self._process_transfer(transaction)

            transaction.status = TransactionStatus.COMPLETED
            transaction.processed_at = datetime.now()

        except (
            InvalidOperationError,
            InsufficientFundsError,
            AccountFrozenError,
            AccountClosedError,
        ) as error:
            transaction.status = TransactionStatus.FAILED
            transaction.failure_reason = str(error)
            transaction.retry_count += 1
            transaction.processed_at = datetime.now()

    def process_queue(self, queue: TransactionQueue) -> None:
        if not isinstance(queue, TransactionQueue):
            raise InvalidOperationError("Queue must be an instance of TransactionQueue")

        while True:
            transaction = queue.get_next_transaction()

            if transaction is None:
                break

            self.process_transaction(transaction)
            queue.remove_transaction(transaction.transaction_id)

    def _convert_amount(
        self,
        amount: float,
        from_currency,
        to_currency,
    ) -> float:
        if from_currency == to_currency:
            return amount

        exchange_rates = {
            ("USD", "EUR"): 0.92,
            ("EUR", "USD"): 1.08,
            ("USD", "RUB"): 90.0,
            ("RUB", "USD"): 0.011,
            ("USD", "KZT"): 450.0,
            ("KZT", "USD"): 0.0022,
            ("EUR", "RUB"): 98.0,
            ("RUB", "EUR"): 0.010,
        }

        rate = exchange_rates.get((from_currency.value, to_currency.value))

        if rate is None:
            raise InvalidOperationError(
                f"Unsupported currency conversion: {from_currency.value} to {to_currency.value}"
            )

        return amount * rate

    def _get_account(self, account_id: str) -> BankAccount:
        if account_id not in self.bank.accounts:
            raise InvalidOperationError("Account doesn't exist")

        return self.bank.accounts[account_id]

    def _process_deposit(self, transaction: Transaction) -> None:
        if transaction.receiver_account_id is None:
            raise InvalidOperationError("Receiver account doesn't exist")

        account = self._get_account(transaction.receiver_account_id)
        account.deposit(transaction.amount)

    def _process_withdraw(self, transaction: Transaction) -> None:
        if transaction.sender_account_id is None:
            raise InvalidOperationError("Sender account doesn't exist")

        account = self._get_account(transaction.sender_account_id)
        account.withdraw(transaction.amount)

    def _process_transfer(self, transaction: Transaction) -> None:
        if transaction.sender_account_id is None:
            raise InvalidOperationError("Sender account doesn't exist")

        if transaction.receiver_account_id is None:
            raise InvalidOperationError("Receiver account doesn't exist")

        sender = self._get_account(transaction.sender_account_id)
        receiver = self._get_account(transaction.receiver_account_id)

        # pre-check both accounts before money movement
        sender._check_account_status()
        receiver._check_account_status()

        total_amount = transaction.amount + transaction.fee

        converted_amount = self._convert_amount(
            transaction.amount,
            sender.currency,
            receiver.currency,
        )

        sender.withdraw(total_amount)
        receiver.deposit(converted_amount)

    def _calculate_fee(self, transaction: Transaction) -> float:
        if transaction.transaction_type == TransactionType.TRANSFER:
            return transaction.amount * 0.01

        return 0.0
