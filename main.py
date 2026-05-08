from src.banking_system.accounts.bank_account import BankAccount
from src.banking_system.exceptions.account_exceptions import AccountFrozenError
from src.banking_system.accounts.enums import AccountStatus

active_account = BankAccount(owner="Roman", balance=1000)
frozen_account = BankAccount(
    owner="Anna",
    balance=500,
    status=AccountStatus.FROZEN,
)

print(active_account)
active_account.deposit(300)
active_account.withdraw(100)
print(active_account)

print(frozen_account)
try:
    frozen_account.deposit(100)
except AccountFrozenError as error:
    print(error)
