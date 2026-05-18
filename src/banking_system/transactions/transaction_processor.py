from datetime import datetime

from ..accounts.bank_account import BankAccount
from ..audit.audit_log import AuditLog
from ..audit.risk_analyzer import RiskAnalyzer
from ..audit.enums import RiskLevel, AuditLevel
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
    def __init__(
        self,
        bank: Bank,
        audit_log: AuditLog,
        risk_analyzer: RiskAnalyzer,
        max_retries: int = 3,
    ) -> None:
        if not isinstance(bank, Bank):
            raise InvalidOperationError("Bank must be an instance of Bank")

        if not isinstance(audit_log, AuditLog):
            raise InvalidOperationError("Audit log must be an instance of AuditLog")

        if not isinstance(risk_analyzer, RiskAnalyzer):
            raise InvalidOperationError(
                "Risk analyzer must be an instance of RiskAnalyzer"
            )

        self.bank = bank
        self.audit_log = audit_log
        self.risk_analyzer = risk_analyzer
        self.max_retries = max_retries

    def process_transaction(self, transaction: Transaction) -> None:
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Transaction must be an instance of Transaction"
            )

        if transaction.status != TransactionStatus.PENDING:
            raise InvalidOperationError("Only pending transactions can be processed")

        risk_level = self.risk_analyzer.analyze_transaction(transaction)

        if risk_level == RiskLevel.HIGH:
            transaction.status = TransactionStatus.FAILED
            transaction.failure_reason = "Transaction blocked by risk analyzer"
            transaction.processed_at = datetime.now()
            transaction.retry_count += 1
            self.audit_log.log(
                level=AuditLevel.CRITICAL,
                message="Transaction blocked by risk analyzer",
                transaction_id=transaction.transaction_id,
                client_id=self._get_client_id_for_transaction(transaction),
            )
            return

        if risk_level == RiskLevel.MEDIUM:
            self.audit_log.log(
                level=AuditLevel.WARNING,
                message="Medium risk transaction detected",
                transaction_id=transaction.transaction_id,
                client_id=self._get_client_id_for_transaction(transaction),
            )

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

            self.audit_log.log(
                level=AuditLevel.INFO,
                message="Transaction completed",
                transaction_id=transaction.transaction_id,
                client_id=self._get_client_id_for_transaction(transaction),
            )

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

            self.audit_log.log(
                level=AuditLevel.ERROR,
                message=str(error),
                transaction_id=transaction.transaction_id,
                client_id=self._get_client_id_for_transaction(transaction),
            )

    def process_queue(self, queue: TransactionQueue) -> None:
        # current implementation has only non-retryable failures\n
        # retry logic is kept for future temporary errors
        if not isinstance(queue, TransactionQueue):
            raise InvalidOperationError("Queue must be an instance of TransactionQueue")

        while True:
            transaction = queue.get_next_transaction()

            if transaction is None:
                break

            self.process_transaction(transaction)

            if transaction.status == TransactionStatus.COMPLETED:
                print(f"[SUCCESS] {transaction.transaction_id}")
                queue.remove_transaction(transaction.transaction_id)

            elif transaction.status == TransactionStatus.FAILED:
                if self._is_retryable_failure(transaction):
                    if transaction.retry_count < self.max_retries:
                        print(f"[RETRY] {transaction.transaction_id}")
                        transaction.status = TransactionStatus.PENDING
                    else:
                        print(f"[FAILED] {transaction.transaction_id}")
                        queue.remove_transaction(transaction.transaction_id)
                else:
                    print(f"[FAILED] {transaction.transaction_id}")
                    queue.remove_transaction(transaction.transaction_id)

    def _is_retryable_failure(self, transaction: Transaction) -> bool:
        # future extension point for temporary failures
        return False

    def _get_client_id_for_transaction(self, transaction: Transaction) -> str | None:
        account_id = transaction.sender_account_id or transaction.receiver_account_id

        if account_id is None:
            return None

        for client in self.bank.clients.values():
            if account_id in client.account_ids:
                return client.client_id

        return None

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
