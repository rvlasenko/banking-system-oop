from src.banking_system.accounts.savings_account import SavingsAccount
from src.banking_system.accounts.premium_account import PremiumAccount
from src.banking_system.accounts.investment_account import InvestmentAccount
from src.banking_system.accounts.enums import AccountStatus
from src.banking_system.exceptions.account_exceptions import (
    AccountFrozenError,
    InsufficientFundsError,
    InvalidOperationError,
)


def main() -> None:
    savings = SavingsAccount(
        owner="Roman",
        balance=1_000,
        min_balance=200,
        monthly_interest_rate=5,
    )

    premium = PremiumAccount(
        owner="Anna",
        balance=100,
        overdraft_limit=500,
        withdraw_limit=1_000,
        fixed_fee=10,
    )

    investment = InvestmentAccount(
        owner="Ivan",
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
        status=AccountStatus.FROZEN,
        min_balance=100,
        monthly_interest_rate=3,
    )

    print("\n--- Initial accounts ---")
    print(savings)
    print(premium)
    print(investment)
    print(frozen_savings)

    print("\n--- Savings account ---")
    savings.deposit(300)
    print("After deposit:", savings)

    savings.withdraw(500)
    print("After withdraw:", savings)

    savings.apply_monthly_interest()
    print("After monthly interest:", savings)

    try:
        savings.withdraw(2_000)
    except InsufficientFundsError as error:
        print("Savings error:", error)

    print("\n--- Premium account ---")
    premium.withdraw(300)
    print("After premium withdraw with fee and overdraft:", premium)

    try:
        premium.withdraw(2_000)
    except (InvalidOperationError, InsufficientFundsError) as error:
        print("Premium error:", error)

    print("\n--- Investment account ---")
    print("Current info:", investment.get_account_info())
    print("Projected yearly growth:", investment.project_yearly_growth())

    investment.withdraw(200)
    print("After withdraw:", investment)

    print("\n--- Frozen account ---")
    try:
        frozen_savings.deposit(100)
    except AccountFrozenError as error:
        print("Frozen account error:", error)


if __name__ == "__main__":
    main()
