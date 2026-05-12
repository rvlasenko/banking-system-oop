from src.banking_system.bank.bank import Bank
from src.banking_system.clients.client import Client
from src.banking_system.accounts.bank_account import BankAccount
from src.banking_system.accounts.savings_account import SavingsAccount
from src.banking_system.accounts.premium_account import PremiumAccount
from src.banking_system.accounts.enums import AccountStatus
from src.banking_system.exceptions.bank_exceptions import InvalidOperationError


def print_accounts(accounts):
    for account in accounts:
        print(account)


def main() -> None:
    bank = Bank()

    roman = Client(
        full_name="Roman Vlasenko",
        age=29,
        pin_code="1234",
        contacts={"email": "roman@example.com"},
    )

    anna = Client(
        full_name="Anna Smith",
        age=34,
        pin_code="5555",
        contacts={"email": "anna@example.com"},
    )

    bank.add_client(roman)
    bank.add_client(anna)

    roman_main = BankAccount(owner=roman.full_name, balance=1_000)
    roman_savings = SavingsAccount(
        owner=roman.full_name,
        balance=2_000,
        min_balance=500,
        monthly_interest_rate=5,
    )

    anna_premium = PremiumAccount(
        owner=anna.full_name,
        balance=300,
        overdraft_limit=500,
        withdraw_limit=1_000,
        fixed_fee=10,
    )

    bank.open_account(roman.client_id, roman_main)
    bank.open_account(roman.client_id, roman_savings)
    bank.open_account(anna.client_id, anna_premium)

    print("\n--- All accounts ---")
    print_accounts(bank.search_accounts())

    print("\n--- Roman accounts ---")
    print_accounts(bank.search_accounts(client_id=roman.client_id))

    print("\n--- Anna accounts ---")
    print_accounts(bank.search_accounts(client_id=anna.client_id))

    print("\n--- Freeze account ---")
    bank.freeze_account(roman_main.account_id)
    print_accounts(bank.search_accounts(status=AccountStatus.FROZEN))

    print("\n--- Authentication attempts ---")
    print("Wrong PIN #1:", bank.authenticate_client(anna.client_id, "0000"))
    print("Wrong PIN #2:", bank.authenticate_client(anna.client_id, "1111"))
    print("Anna suspicious:", anna.is_suspicious)
    print("Wrong PIN #3:", bank.authenticate_client(anna.client_id, "2222"))
    print("Anna status:", anna.status.value)

    try:
        bank.authenticate_client(anna.client_id, "5555")
    except InvalidOperationError as error:
        print("Blocked auth error:", error)

    print("\n--- Total bank balance ---")
    print(bank.get_total_balance())

    print("\n--- Clients ranking ---")
    print(bank.get_clients_ranking())

    print("\n--- Close and unfreeze check ---")
    bank.close_account(roman_main.account_id)

    try:
        bank.unfreeze_account(roman_main.account_id)
    except InvalidOperationError as error:
        print("Unfreeze error:", error)


if __name__ == "__main__":
    main()
