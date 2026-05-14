from datetime import datetime, timedelta

from ..accounts.bank_account import BankAccount
from ..accounts.premium_account import PremiumAccount
from ..accounts.enums import AccountStatus, Currency
from ..bank.bank import Bank
from ..clients.client import Client
from ..transactions.enums import (
    TransactionPriority,
    TransactionType,
)
from ..transactions.transaction import Transaction
from ..transactions.transaction_processor import TransactionProcessor
from ..transactions.transaction_queue import TransactionQueue


def _print_accounts(title: str, accounts: list[BankAccount]) -> None:
    print(f"\n--- {title} ---")
    for account in accounts:
        print(account)


def _print_transactions(title: str, transactions: list[Transaction]) -> None:
    print(f"\n--- {title} ---")
    for transaction in transactions:
        print(transaction.get_transaction_info())


def run_day4_demo() -> None:
    print("\n========== Day 4: Transactions and Queue demo ==========")

    bank = Bank()
    queue = TransactionQueue()
    processor = TransactionProcessor(bank)

    roman = Client("Roman Vlasenko", age=29, pin_code="1234")
    anna = Client("Anna Smith", age=34, pin_code="5555")
    ivan = Client("Ivan Petrov", age=41, pin_code="7777")

    bank.add_client(roman)
    bank.add_client(anna)
    bank.add_client(ivan)

    roman_usd = BankAccount(owner=roman.full_name, balance=1_000, currency=Currency.USD)
    roman_eur = BankAccount(owner=roman.full_name, balance=500, currency=Currency.EUR)

    anna_usd = PremiumAccount(
        owner=anna.full_name,
        balance=100,
        currency=Currency.USD,
        overdraft_limit=500,
        withdraw_limit=1_000,
        fixed_fee=10,
    )

    ivan_usd = BankAccount(owner=ivan.full_name, balance=300, currency=Currency.USD)
    frozen_account = BankAccount(
        owner=ivan.full_name,
        balance=200,
        currency=Currency.USD,
        status=AccountStatus.FROZEN,
    )

    bank.open_account(roman.client_id, roman_usd)
    bank.open_account(roman.client_id, roman_eur)
    bank.open_account(anna.client_id, anna_usd)
    bank.open_account(ivan.client_id, ivan_usd)
    bank.open_account(ivan.client_id, frozen_account)

    _print_accounts(
        "Initial accounts",
        [roman_usd, roman_eur, anna_usd, ivan_usd, frozen_account],
    )

    transactions = [
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=200,
            currency=Currency.USD,
            receiver_account_id=roman_usd.account_id,
            priority=TransactionPriority.NORMAL,
        ),
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=150,
            currency=Currency.USD,
            sender_account_id=roman_usd.account_id,
            priority=TransactionPriority.NORMAL,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=100,
            currency=Currency.USD,
            sender_account_id=roman_usd.account_id,
            receiver_account_id=ivan_usd.account_id,
            priority=TransactionPriority.HIGH,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=100,
            currency=Currency.USD,
            sender_account_id=roman_usd.account_id,
            receiver_account_id=roman_eur.account_id,
            priority=TransactionPriority.HIGH,
        ),
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=350,
            currency=Currency.USD,
            sender_account_id=anna_usd.account_id,
            priority=TransactionPriority.NORMAL,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=10_000,
            currency=Currency.USD,
            sender_account_id=ivan_usd.account_id,
            receiver_account_id=roman_usd.account_id,
            priority=TransactionPriority.HIGH,
        ),
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=50,
            currency=Currency.USD,
            receiver_account_id=frozen_account.account_id,
            priority=TransactionPriority.NORMAL,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=50,
            currency=Currency.USD,
            sender_account_id=roman_usd.account_id,
            receiver_account_id=frozen_account.account_id,
            priority=TransactionPriority.NORMAL,
        ),
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=999,
            currency=Currency.USD,
            receiver_account_id=roman_usd.account_id,
            priority=TransactionPriority.LOW,
            execute_after=datetime.now() + timedelta(hours=1),
        ),
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=25,
            currency=Currency.USD,
            sender_account_id=ivan_usd.account_id,
            priority=TransactionPriority.LOW,
        ),
    ]

    for transaction in transactions:
        queue.add_transaction(transaction)

    cancelled_transaction = transactions[-1]
    queue.cancel_transaction(cancelled_transaction.transaction_id)

    _print_transactions("Transactions before processing", transactions)

    print("\n--- Queue processing ---")
    processor.process_queue(queue)

    _print_transactions("Transactions after processing", transactions)

    _print_accounts(
        "Final accounts",
        [roman_usd, roman_eur, anna_usd, ivan_usd, frozen_account],
    )

    print("\n--- Queue state after processing ---")
    print(f"Transactions left in queue: {len(queue.transactions)}")
    for transaction in queue.transactions:
        print(transaction.get_transaction_info())
