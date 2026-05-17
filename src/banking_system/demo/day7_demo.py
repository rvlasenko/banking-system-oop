from ..accounts.bank_account import BankAccount
from ..accounts.enums import Currency
from ..audit.audit_log import AuditLog
from ..audit.enums import AuditLevel
from ..bank.bank import Bank
from ..clients.client import Client
from ..reports.report_builder import ReportBuilder
from ..transactions.enums import TransactionStatus, TransactionType
from ..transactions.transaction import Transaction


def run_day7_demo() -> None:
    print("\n========== Day 7: Reports and Visualization demo ==========")

    bank = Bank()
    audit_log = AuditLog()

    roman = Client(
        full_name="Roman Vlasenko",
        age=29,
        pin_code="1234",
        client_id="C-ROMAN",
    )

    anna = Client(
        full_name="Anna Smith",
        age=34,
        pin_code="5555",
        client_id="C-ANNA",
    )

    ivan = Client(
        full_name="Ivan Petrov",
        age=41,
        pin_code="7777",
        client_id="C-IVAN",
    )

    bank.add_client(roman)
    bank.add_client(anna)
    bank.add_client(ivan)

    roman_account = BankAccount(
        owner=roman.full_name,
        account_id="A-ROMAN",
        balance=1_000,
        currency=Currency.USD,
    )

    anna_account = BankAccount(
        owner=anna.full_name,
        account_id="A-ANNA",
        balance=2_500,
        currency=Currency.USD,
    )

    ivan_account = BankAccount(
        owner=ivan.full_name,
        account_id="A-IVAN",
        balance=1_800,
        currency=Currency.USD,
    )

    bank.open_account(roman.client_id, roman_account)
    bank.open_account(anna.client_id, anna_account)
    bank.open_account(ivan.client_id, ivan_account)

    transactions = [
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=500,
            currency=Currency.USD,
            receiver_account_id=roman_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=120,
            currency=Currency.USD,
            sender_account_id=roman_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=300,
            currency=Currency.USD,
            receiver_account_id=roman_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=80,
            currency=Currency.USD,
            sender_account_id=roman_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=200,
            currency=Currency.USD,
            receiver_account_id=roman_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=400,
            currency=Currency.USD,
            sender_account_id=anna_account.account_id,
            receiver_account_id=ivan_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.TRANSFER,
            amount=10_000,
            currency=Currency.USD,
            sender_account_id=roman_account.account_id,
            receiver_account_id=anna_account.account_id,
        ),
        Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=700,
            currency=Currency.USD,
            receiver_account_id=ivan_account.account_id,
        ),
    ]

    transactions[0].status = TransactionStatus.COMPLETED
    transactions[1].status = TransactionStatus.COMPLETED
    transactions[2].status = TransactionStatus.COMPLETED
    transactions[3].status = TransactionStatus.COMPLETED
    transactions[4].status = TransactionStatus.COMPLETED
    transactions[5].status = TransactionStatus.CANCELLED
    transactions[6].status = TransactionStatus.FAILED
    transactions[7].status = TransactionStatus.PENDING

    audit_log.log(
        level=AuditLevel.INFO,
        message="Demo transaction completed",
        transaction_id=transactions[0].transaction_id,
        client_id=roman.client_id,
    )

    audit_log.log(
        level=AuditLevel.WARNING,
        message="Medium risk transaction detected",
        transaction_id=transactions[6].transaction_id,
        client_id=roman.client_id,
    )

    audit_log.log(
        level=AuditLevel.ERROR,
        message="Transaction failed during demo",
        transaction_id=transactions[6].transaction_id,
        client_id=roman.client_id,
    )

    builder = ReportBuilder(
        bank=bank,
        audit_log=audit_log,
        transactions=transactions,
    )

    bank_report = builder.build_bank_report()
    client_report = builder.build_client_report(roman.client_id)
    risk_report = builder.build_risk_report()

    full_report = {
        "bank_report": bank_report,
        "client_report": client_report,
        "risk_report": risk_report,
    }

    print("\n--- Text report ---")
    print(builder.build_text_report("Bank Report", bank_report))

    builder.export_to_json(full_report)

    builder.export_to_csv(bank_report["top_clients"])

    builder.save_charts(roman.client_id)

    print("\n--- Exported files ---")
    print("JSON: reports/json/report.json")
    print("CSV: reports/csv/report.csv")
    print("Charts: reports/charts/")
