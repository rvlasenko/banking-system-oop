from dataclasses import dataclass
from datetime import datetime, timedelta

from ..accounts.bank_account import BankAccount
from ..accounts.enums import AccountStatus, Currency
from ..accounts.investment_account import InvestmentAccount
from ..accounts.premium_account import PremiumAccount
from ..accounts.savings_account import SavingsAccount
from ..audit.audit_log import AuditLog
from ..audit.risk_analyzer import RiskAnalyzer
from ..bank.bank import Bank
from ..clients.client import Client
from ..transactions.enums import TransactionPriority, TransactionType
from ..transactions.transaction import Transaction
from ..transactions.transaction_processor import TransactionProcessor
from ..transactions.transaction_queue import TransactionQueue


@dataclass
class DemoContext:
    bank: Bank
    audit_log: AuditLog
    risk_analyzer: RiskAnalyzer
    queue: TransactionQueue
    processor: TransactionProcessor


def run_day6_demo() -> None:
    context = setup_bank()

    clients = create_clients(context)
    accounts = create_accounts(context, clients)
    transactions = create_transactions(accounts)

    run_simulation(context, transactions)
    print_logging(context)
    print_user_scenarios(context, transactions)
    print_reports(context, transactions)


def setup_bank() -> DemoContext:
    bank = Bank()
    audit_log = AuditLog()
    risk_analyzer = RiskAnalyzer()
    queue = TransactionQueue()
    processor = TransactionProcessor(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer,
    )

    return DemoContext(
        bank=bank,
        audit_log=audit_log,
        risk_analyzer=risk_analyzer,
        queue=queue,
        processor=processor,
    )


def create_clients(context: DemoContext) -> list[Client]:
    clients = [
        Client(
            full_name="Roman Vlasenko",
            age=29,
            pin_code="1234",
        ),
        Client(
            full_name="Anna Smith",
            age=34,
            pin_code="5555",
        ),
        Client(
            full_name="Ivan Petrov",
            age=41,
            pin_code="7777",
        ),
        Client(
            full_name="Maria Garcia",
            age=26,
            pin_code="2222",
        ),
        Client(
            full_name="John Walker",
            age=38,
            pin_code="9999",
        ),
        Client(
            full_name="Emma Brown",
            age=31,
            pin_code="4444",
        ),
        Client(
            full_name="Kenji Tanaka",
            age=45,
            pin_code="8888",
        ),
    ]

    for client in clients:
        context.bank.add_client(client)

    return clients


def create_accounts(
    context: DemoContext,
    clients: list[Client],
) -> list[BankAccount]:
    accounts: list[BankAccount] = [
        BankAccount(
            owner=clients[0].full_name,
            balance=15_000,
            currency=Currency.USD,
        ),
        SavingsAccount(
            owner=clients[0].full_name,
            balance=8_000,
            currency=Currency.EUR,
            monthly_interest_rate=0.02,
            min_balance=500,
        ),
        PremiumAccount(
            owner=clients[1].full_name,
            balance=3_000,
            currency=Currency.USD,
            overdraft_limit=2_000,
            withdraw_limit=5_000,
            fixed_fee=25,
        ),
        BankAccount(
            owner=clients[1].full_name,
            balance=1_500,
            currency=Currency.EUR,
        ),
        InvestmentAccount(
            owner=clients[2].full_name,
            balance=12_000,
            currency=Currency.USD,
        ),
        BankAccount(
            owner=clients[2].full_name,
            balance=500,
            currency=Currency.RUB,
        ),
        SavingsAccount(
            owner=clients[3].full_name,
            balance=4_500,
            currency=Currency.USD,
            monthly_interest_rate=0.03,
            min_balance=300,
        ),
        BankAccount(
            owner=clients[3].full_name,
            balance=2_200,
            currency=Currency.KZT,
        ),
        PremiumAccount(
            owner=clients[4].full_name,
            balance=20_000,
            currency=Currency.USD,
            overdraft_limit=5_000,
            withdraw_limit=10_000,
            fixed_fee=50,
        ),
        InvestmentAccount(
            owner=clients[4].full_name,
            balance=7_000,
            currency=Currency.EUR,
        ),
        BankAccount(
            owner=clients[5].full_name,
            balance=900,
            currency=Currency.USD,
        ),
        SavingsAccount(
            owner=clients[5].full_name,
            balance=1_800,
            currency=Currency.EUR,
            monthly_interest_rate=0.01,
            min_balance=200,
        ),
        BankAccount(
            owner=clients[6].full_name,
            balance=11_000,
            currency=Currency.USD,
        ),
        InvestmentAccount(
            owner=clients[6].full_name,
            balance=25_000,
            currency=Currency.USD,
        ),
    ]

    client_accounts = {
        clients[0].client_id: [accounts[0], accounts[1]],
        clients[1].client_id: [accounts[2], accounts[3]],
        clients[2].client_id: [accounts[4], accounts[5]],
        clients[3].client_id: [accounts[6], accounts[7]],
        clients[4].client_id: [accounts[8], accounts[9]],
        clients[5].client_id: [accounts[10], accounts[11]],
        clients[6].client_id: [accounts[12], accounts[13]],
    }

    for client_id, client_accounts_list in client_accounts.items():
        for account in client_accounts_list:
            context.bank.open_account(client_id, account)

    return accounts


def create_transactions(
    accounts: list[BankAccount],
) -> list[Transaction]:
    transactions: list[Transaction] = []

    # shortcuts
    roman_main = accounts[0]
    anna_premium = accounts[2]
    anna_eur = accounts[3]
    ivan_investment = accounts[4]
    ivan_rub = accounts[5]

    # ==========
    # Normal operations
    # ==========

    transactions.extend(
        [
            Transaction(
                transaction_type=TransactionType.DEPOSIT,
                amount=500,
                currency=Currency.USD,
                receiver_account_id=roman_main.account_id,
            ),
            Transaction(
                transaction_type=TransactionType.WITHDRAW,
                amount=200,
                currency=Currency.USD,
                sender_account_id=roman_main.account_id,
            ),
            Transaction(
                transaction_type=TransactionType.TRANSFER,
                amount=300,
                currency=Currency.USD,
                sender_account_id=roman_main.account_id,
                receiver_account_id=anna_premium.account_id,
            ),
        ]
    )

    # ==========
    # Suspicious operations
    # ==========

    # large transfer
    transactions.append(
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=15_000,
            currency=Currency.USD,
            sender_account_id=roman_main.account_id,
            receiver_account_id=ivan_investment.account_id,
            priority=TransactionPriority.HIGH,
        )
    )

    # night transaction
    night_transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=100,
        currency=Currency.USD,
        sender_account_id=roman_main.account_id,
        receiver_account_id=anna_eur.account_id,
    )

    night_transaction.created_at = datetime.now().replace(
        hour=2,
        minute=0,
        second=0,
    )

    transactions.append(night_transaction)

    # frequent operations
    for _ in range(6):
        transactions.append(
            Transaction(
                transaction_type=TransactionType.TRANSFER,
                amount=10,
                currency=Currency.USD,
                sender_account_id=roman_main.account_id,
                receiver_account_id=anna_premium.account_id,
            )
        )

    # ==========
    # Failed operations
    # ==========

    # insufficient funds
    transactions.append(
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=999_999,
            currency=Currency.USD,
            sender_account_id=ivan_rub.account_id,
        )
    )

    # frozen account
    frozen_account = accounts[10]
    frozen_account.status = AccountStatus.FROZEN

    transactions.append(
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=100,
            currency=Currency.USD,
            sender_account_id=anna_premium.account_id,
            receiver_account_id=frozen_account.account_id,
        )
    )

    # ==========
    # Delayed transaction
    # ==========

    delayed_transaction = Transaction(
        transaction_type=TransactionType.DEPOSIT,
        amount=999,
        currency=Currency.USD,
        receiver_account_id=roman_main.account_id,
        execute_after=datetime.now() + timedelta(hours=1),
    )

    transactions.append(delayed_transaction)

    # ==========
    # Bulk traffic
    # ==========

    safe_accounts = [
        account
        for account in accounts
        if account.status == AccountStatus.ACTIVE and account.currency == Currency.USD
    ]

    for i in range(20):
        sender = safe_accounts[i % len(safe_accounts)]
        receiver = safe_accounts[(i + 1) % len(safe_accounts)]

        transactions.append(
            Transaction(
                transaction_type=TransactionType.TRANSFER,
                amount=50 + i * 5,
                currency=sender.currency,
                sender_account_id=sender.account_id,
                receiver_account_id=receiver.account_id,
            )
        )

    return transactions


def run_simulation(
    context: DemoContext,
    transactions: list[Transaction],
) -> None:
    _print_section("Simulation")

    for transaction in transactions:
        context.queue.add_transaction(transaction)

    print(f"Added to queue: {len(transactions)} transactions")

    # cancel a couple of pending transactions
    transactions_to_cancel = transactions[-2:]

    for transaction in transactions_to_cancel:
        context.queue.cancel_transaction(transaction.transaction_id)
        print(f"[CANCELLED] {transaction.transaction_id}")

    context.processor.process_queue(context.queue)

    completed = len([tx for tx in transactions if tx.status.value == "completed"])
    failed = len([tx for tx in transactions if tx.status.value == "failed"])
    cancelled = len([tx for tx in transactions if tx.status.value == "cancelled"])
    pending = len([tx for tx in transactions if tx.status.value == "pending"])

    print(f"Completed: {completed}")
    print(f"Failed / blocked: {failed}")
    print(f"Cancelled: {cancelled}")
    print(f"Pending delayed: {pending}")


def print_reports(
    context: DemoContext,
    transactions: list[Transaction],
) -> None:
    _print_section("Reports")

    _print_subsection("Top 3 clients")
    top_clients = context.bank.get_clients_ranking()[:3]

    for index, client in enumerate(top_clients, start=1):
        print(
            f"{index}. {client['full_name']} "
            f"({client['client_id']}) — "
            f"{client['total_balance']:.2f}"
        )

    _print_subsection("Transaction statistics")
    completed = len([tx for tx in transactions if tx.status.value == "completed"])
    failed = len([tx for tx in transactions if tx.status.value == "failed"])
    cancelled = len([tx for tx in transactions if tx.status.value == "cancelled"])
    pending = len([tx for tx in transactions if tx.status.value == "pending"])

    print(f"Completed: {completed}")
    print(f"Failed / blocked: {failed}")
    print(f"Cancelled: {cancelled}")
    print(f"Pending delayed: {pending}")

    _print_subsection("Bank total balance")
    print(f"Total bank balance: {context.bank.get_total_balance():.2f}")

    _print_subsection("Queue state")
    print(f"Transactions left in queue: {len(context.queue.transactions)}")


def print_logging(context: DemoContext) -> None:
    _print_section("Logging")

    print(f"Audit entries created: {len(context.audit_log.entries)}")

    statistics = context.audit_log.get_error_statistics()

    for level, count in statistics.items():
        print(f"{level}: {count}")


def print_user_scenarios(
    context: DemoContext,
    transactions: list[Transaction],
) -> None:
    _print_section("User Scenarios")

    demo_client = list(context.bank.clients.values())[0]

    _print_subsection("Client accounts")
    print(f"Client: {demo_client.full_name} ({demo_client.client_id}) \n")

    for account_id in demo_client.account_ids:
        account = context.bank.accounts[account_id]
        print(account)

    _print_subsection("Client transaction history")
    client_transactions = _get_client_transactions(demo_client, transactions)

    for transaction in client_transactions[:10]:
        print(
            f"{transaction.transaction_type.value} | "
            f"{transaction.amount} {transaction.currency.value} | "
            f"{transaction.status.value} | "
            f"fee: {transaction.fee}"
        )

    _print_subsection("Client suspicious operations")
    suspicious_entries = _get_client_suspicious_entries(context, demo_client)

    print(f"Suspicious events for client: {len(suspicious_entries)}")

    for entry in suspicious_entries[:5]:
        print(
            f"[{entry['level'].upper()}] "
            f"{entry['message']} "
            f"(transaction: {entry['transaction_id']})"
        )


def _get_client_transactions(
    client: Client,
    transactions: list[Transaction],
) -> list[Transaction]:
    return [
        transaction
        for transaction in transactions
        if transaction.sender_account_id in client.account_ids
        or transaction.receiver_account_id in client.account_ids
    ]


def _get_client_suspicious_entries(
    context: DemoContext,
    client: Client,
) -> list[dict]:
    return [
        entry
        for entry in context.audit_log.get_suspicious_entries()
        if entry["client_id"] == client.client_id
    ]


def _print_section(title: str) -> None:
    print(f"\n========== {title} ==========")


def _print_subsection(title: str) -> None:
    print(f"\n--- {title} ---")
