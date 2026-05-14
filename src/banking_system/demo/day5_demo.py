from datetime import datetime

from ..accounts.bank_account import BankAccount
from ..accounts.enums import Currency
from ..audit.audit_log import AuditLog
from ..audit.risk_analyzer import RiskAnalyzer
from ..bank.bank import Bank
from ..clients.client import Client
from ..transactions.enums import TransactionPriority, TransactionType
from ..transactions.transaction import Transaction
from ..transactions.transaction_processor import TransactionProcessor
from ..transactions.transaction_queue import TransactionQueue


def _print_entries(title: str, entries: list[dict]) -> None:
    print(f"\n--- {title} ---")
    for entry in entries:
        print(entry)


def run_day5_demo() -> None:
    print("\n========== Day 5: Audit and Risk Analysis demo ==========")

    bank = Bank()
    audit_log = AuditLog()
    risk_analyzer = RiskAnalyzer()
    queue = TransactionQueue()
    processor = TransactionProcessor(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer,
    )

    roman = Client(
        full_name="Roman Vlasenko",
        age=29,
        pin_code="1234",
    )

    anna = Client(
        full_name="Anna Smith",
        age=34,
        pin_code="5555",
    )

    bank.add_client(roman)
    bank.add_client(anna)

    roman_account = BankAccount(
        owner=roman.full_name,
        balance=20_000,
        currency=Currency.USD,
    )

    anna_account = BankAccount(
        owner=anna.full_name,
        balance=1_000,
        currency=Currency.USD,
    )

    bank.open_account(roman.client_id, roman_account)
    bank.open_account(anna.client_id, anna_account)

    normal_deposit = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=500,
        currency=Currency.USD,
        receiver_account_id=roman_account.account_id,
        priority=TransactionPriority.NORMAL,
    )

    normal_transfer = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=300,
        currency=Currency.USD,
        sender_account_id=roman_account.account_id,
        receiver_account_id=anna_account.account_id,
        priority=TransactionPriority.NORMAL,
    )

    large_transfer = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=15_000,
        currency=Currency.USD,
        sender_account_id=roman_account.account_id,
        receiver_account_id=anna_account.account_id,
        priority=TransactionPriority.HIGH,
    )

    night_transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=100,
        currency=Currency.USD,
        sender_account_id=roman_account.account_id,
        receiver_account_id=anna_account.account_id,
        priority=TransactionPriority.NORMAL,
    )
    night_transaction.created_at = datetime.now().replace(hour=2, minute=0, second=0)

    frequent_transactions = [
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=10,
            currency=Currency.USD,
            sender_account_id=roman_account.account_id,
            receiver_account_id=anna_account.account_id,
            priority=TransactionPriority.NORMAL,
        )
        for _ in range(6)
    ]

    transactions = [
        normal_deposit,
        normal_transfer,
        large_transfer,
        night_transaction,
        *frequent_transactions,
    ]

    for transaction in transactions:
        queue.add_transaction(transaction)

    print("\n--- Initial accounts ---")
    print(roman_account)
    print(anna_account)

    processor.process_queue(queue)

    print("\n--- Final accounts ---")
    print(roman_account)
    print(anna_account)

    _print_entries("All audit entries", audit_log.entries)
    _print_entries("Suspicious audit entries", audit_log.get_suspicious_entries())

    print("\n--- Error statistics ---")
    print(audit_log.get_error_statistics())

    print("\n--- Roman risk profile ---")
    print(audit_log.get_client_risk_profile(roman.client_id))

    print("\n--- Anna risk profile ---")
    print(audit_log.get_client_risk_profile(anna.client_id))

    audit_log.save_to_file()
    print("\nAudit log saved to logs/audit.log")
