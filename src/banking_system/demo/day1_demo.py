from ..accounts.bank_account import BankAccount
from ..accounts.enums import AccountStatus
from ..exceptions.account_exceptions import (
    AccountFrozenError,
    InsufficientFundsError,
)
from ..exceptions.invalid_operation import InvalidOperationError


def run_day1_demo() -> None:
    print("\n========== Day 1: Basic BankAccount demo ==========")

    active_account = BankAccount(
        owner="Roman Vlasenko",
        balance=1_000,
    )

    frozen_account = BankAccount(
        owner="Frozen Client",
        balance=500,
        status=AccountStatus.FROZEN,
    )

    print("\n--- Initial accounts ---")
    print(active_account)
    print(frozen_account)

    print("\n--- Valid deposit and withdraw ---")
    active_account.deposit(300)
    print("After deposit:", active_account)

    active_account.withdraw(200)
    print("After withdraw:", active_account)

    print("\n--- Invalid withdraw: insufficient funds ---")
    try:
        active_account.withdraw(10_000)
    except InsufficientFundsError as error:
        print("Expected error:", error)

    print("\n--- Frozen account operations ---")
    try:
        frozen_account.deposit(100)
    except AccountFrozenError as error:
        print("Expected deposit error:", error)

    try:
        frozen_account.withdraw(100)
    except AccountFrozenError as error:
        print("Expected withdraw error:", error)

    print("\n--- Invalid amount ---")
    try:
        active_account.deposit(-50)
    except InvalidOperationError as error:
        print("Expected amount error:", error)

    print("\n--- Account info ---")
    print(active_account.get_account_info())
