import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt

from ..audit.audit_log import AuditLog
from ..bank.bank import Bank
from ..exceptions.invalid_operation import InvalidOperationError
from ..transactions.enums import TransactionStatus
from ..transactions.transaction import Transaction


class ReportBuilder:
    def __init__(
        self, bank: Bank, audit_log: AuditLog, transactions: list[Transaction]
    ):
        if not isinstance(bank, Bank):
            raise InvalidOperationError("Bank must be an instance of Bank")

        if not isinstance(audit_log, AuditLog):
            raise InvalidOperationError("Audit log must be an instance of AuditLog")

        if not isinstance(transactions, list):
            raise InvalidOperationError("Transactions must be a list")

        if not all(
            isinstance(transaction, Transaction) for transaction in transactions
        ):
            raise InvalidOperationError("All items must be Transaction instances")

        self.bank = bank
        self.audit_log = audit_log
        self.transactions = transactions

    def build_bank_report(self) -> dict:
        transaction_statistics = {}

        for status in TransactionStatus:
            transaction_statistics[status.value] = len(
                [
                    transaction
                    for transaction in self.transactions
                    if transaction.status == status
                ]
            )

        return {
            "total_clients": len(self.bank.clients),
            "total_accounts": len(self.bank.accounts),
            "total_balance": self.bank.get_total_balance(),
            "top_clients": self.bank.get_clients_ranking()[:3],
            "transaction_statistics": transaction_statistics,
        }

    def build_client_report(self, client_id: str) -> dict:
        if client_id not in self.bank.clients:
            raise InvalidOperationError("Client doesn't exist")

        client = self.bank.clients[client_id]
        accounts = [self.bank.accounts[account_id] for account_id in client.account_ids]
        total_balance = sum(account._balance for account in accounts)

        transaction_history = [
            transaction.get_transaction_info()
            for transaction in self.transactions
            if transaction.sender_account_id in client.account_ids
            or transaction.receiver_account_id in client.account_ids
        ]

        return {
            "client_id": client_id,
            "full_name": client.full_name,
            "accounts": [account.get_account_info() for account in accounts],
            "total_balance": total_balance,
            "transaction_history": transaction_history,
            "risk_profile": self.audit_log.get_client_risk_profile(client_id),
        }

    def build_risk_report(self) -> dict:
        suspicious_entries = self.audit_log.get_suspicious_entries()
        error_statistics = self.audit_log.get_error_statistics()

        return {
            "suspicious_entries": suspicious_entries,
            "error_statistics": error_statistics,
            "total_suspicious_events": len(suspicious_entries),
        }

    def export_to_csv(
        self,
        rows: list[dict],
        file_path: str | None = None,
    ) -> None:
        if not isinstance(rows, list):
            raise InvalidOperationError("Rows must be a list")

        if not rows:
            raise InvalidOperationError("Rows cannot be empty")

        if not all(isinstance(row, dict) for row in rows):
            raise InvalidOperationError("All rows must be dictionaries")

        if file_path is None:
            target_path = self._build_report_path("csv", "report.csv")
        else:
            target_path = Path(file_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)

        with target_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    def export_to_json(self, data: dict, file_path: str | None = None) -> None:
        if file_path is None:
            target_path = self._build_report_path("json", "report.json")
        else:
            target_path = Path(file_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)

        with open(target_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def build_text_report(self, title: str, data: dict) -> str:
        lines = [f"=== {title} ==="]

        for key, value in data.items():
            lines.append(f"\n{key}:")

            if isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        formatted_item = ", ".join(
                            f"{item_key}: {item_value}"
                            for item_key, item_value in item.items()
                        )
                        lines.append(f"  - {formatted_item}")
                    else:
                        lines.append(f"  - {item}")

            elif isinstance(value, dict):
                for nested_key, nested_value in value.items():
                    lines.append(f"  {nested_key}: {nested_value}")

            else:
                lines.append(f"  {value}")

        return "\n".join(lines)

    def save_transaction_status_chart(self, file_path: str | None = None) -> None:
        bank_report = self.build_bank_report()
        statistics = bank_report["transaction_statistics"]

        filtered_statistics = {
            label: value for label, value in statistics.items() if value > 0
        }

        labels = list(filtered_statistics.keys())
        values = list(filtered_statistics.values())

        if file_path is None:
            target_path = self._build_report_path("charts", "transaction_statuses.png")
        else:
            target_path = Path(file_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure()
        plt.pie(values, labels=labels, autopct="%1.1f%%")
        plt.title("Transaction statuses")
        plt.savefig(target_path)
        plt.close()

    def save_top_clients_chart(
        self,
        file_path: str | None = None,
    ) -> None:
        bank_report = self.build_bank_report()
        top_clients = bank_report["top_clients"]

        labels = [client["full_name"] for client in top_clients]

        balances = [client["total_balance"] for client in top_clients]

        if file_path is None:
            target_path = self._build_report_path("charts", "top_clients.png")
        else:
            target_path = Path(file_path)

        target_path.parent.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(8, 5))

        plt.bar(labels, balances)

        plt.title("Top clients by balance")
        plt.xlabel("Clients")
        plt.ylabel("Balance")

        plt.savefig(target_path)
        plt.close()

    def save_client_balance_chart(
        self,
        client_id: str,
        file_path: str | None = None,
    ) -> None:
        if client_id not in self.bank.clients:
            raise InvalidOperationError("Client doesn't exist")

        client = self.bank.clients[client_id]

        account_ids = set(client.account_ids)

        balance = 0
        balances = []
        transaction_numbers = []

        completed_transactions = [
            transaction
            for transaction in self.transactions
            if transaction.status == TransactionStatus.COMPLETED
        ]

        for index, transaction in enumerate(
            completed_transactions,
            start=1,
        ):
            if transaction.receiver_account_id in account_ids:
                balance += transaction.amount

            if transaction.sender_account_id in account_ids:
                balance -= transaction.amount + transaction.fee

            if (
                transaction.sender_account_id in account_ids
                or transaction.receiver_account_id in account_ids
            ):
                balances.append(balance)
                transaction_numbers.append(index)

        if not balances:
            raise InvalidOperationError("No completed transactions for chart")

        if file_path is None:
            target_path = self._build_report_path(
                "charts",
                "client_balance.png",
            )
        else:
            target_path = Path(file_path)

        plt.figure(figsize=(8, 5))

        plt.plot(
            transaction_numbers,
            balances,
            marker="o",
        )

        plt.title(f"Balance movement for {client.full_name}")

        plt.xlabel("Transaction number")
        plt.ylabel("Balance movement")

        plt.savefig(target_path)

        plt.close()

    def save_charts(self, client_id: str) -> None:
        self.save_transaction_status_chart()
        self.save_top_clients_chart()
        self.save_client_balance_chart(client_id)

    def _build_report_path(
        self,
        category: str,
        filename: str,
    ) -> Path:
        project_root = Path(__file__).resolve().parents[3]

        target_path = project_root / "reports" / category / filename

        target_path.parent.mkdir(parents=True, exist_ok=True)

        return target_path
