from ..accounts.savings_account import SavingsAccount
from ..accounts.premium_account import PremiumAccount
from ..accounts.investment_account import InvestmentAccount
from ..accounts.enums import AccountStatus
from ..exceptions.account_exceptions import (
    AccountFrozenError,
    InsufficientFundsError,
)
from ..exceptions.invalid_operation import InvalidOperationError


def run_day2_demo() -> None:
    print("\n========== Day 2: Advanced Accounts demo ==========")

    savings_account = SavingsAccount(
        owner="Roman Vlasenko",
        balance=1_000,
        min_balance=200,
        monthly_interest_rate=5,
    )

    premium_account = PremiumAccount(
        owner="Anna Smith",
        balance=100,
        overdraft_limit=500,
        withdraw_limit=1_000,
        fixed_fee=10,
    )

    investment_account = InvestmentAccount(
        owner="Ivan Petrov",
        balance=700,
        portfolio={
            "stocks": 1_000,
            "bonds": 500,
            "etf": 700,
        },
    )

    frozen_savings = SavingsAccount(
        owner="Frozen Client",
        balance=500,
        min_balance=100,
        monthly_interest_rate=3,
        status=AccountStatus.FROZEN,
    )

    print("\n--- Initial accounts ---")
    print(savings_account)
    print(premium_account)
    print(investment_account)
    print(frozen_savings)

    print("\n--- SavingsAccount operations ---")
    savings_account.deposit(300)
    print("After deposit:", savings_account)

    savings_account.withdraw(500)
    print("After withdraw:", savings_account)

    savings_account.apply_monthly_interest()
    print("After monthly interest:", savings_account)

    try:
        savings_account.withdraw(10_000)
    except InsufficientFundsError as error:
        print("Expected savings error:", error)

    print("\n--- PremiumAccount operations ---")
    premium_account.withdraw(300)
    print("After overdraft withdraw:", premium_account)

    try:
        premium_account.withdraw(5_000)
    except InvalidOperationError as error:
        print("Expected premium error:", error)

    print("\n--- InvestmentAccount operations ---")
    print("Current info:")
    print(investment_account.get_account_info())

    print("\nProjected yearly growth:")
    print(investment_account.project_yearly_growth())

    investment_account.withdraw(200)
    print("After withdraw:", investment_account)

    print("\n--- Frozen account operations ---")
    try:
        frozen_savings.deposit(100)
    except AccountFrozenError as error:
        print("Expected frozen deposit error:", error)

    try:
        frozen_savings.withdraw(100)
    except AccountFrozenError as error:
        print("Expected frozen withdraw error:", error)
