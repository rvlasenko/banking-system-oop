from src.banking_system.demo.day1_demo import run_day1_demo
from src.banking_system.demo.day2_demo import run_day2_demo
from src.banking_system.demo.day3_demo import run_day3_demo
from src.banking_system.demo.day4_demo import run_day4_demo
from src.banking_system.demo.day5_demo import run_day5_demo
from src.banking_system.demo.day6_demo import run_day6_demo


DEMOS = {
    "1": ("Day 1: Basic BankAccount", run_day1_demo),
    "2": ("Day 2: Advanced Accounts", run_day2_demo),
    "3": ("Day 3: Bank System", run_day3_demo),
    "4": ("Day 4: Transactions and Queue", run_day4_demo),
    "5": ("Day 5: Audit and Risk Analysis", run_day5_demo),
    "6": ("Day 6: Full System Demo", run_day6_demo),
}


def main() -> None:
    print("\n=== Banking System Demos ===\n")

    for key, (label, _) in DEMOS.items():
        print(f"{key}. {label}")

    choice = input("\nSelect demo: ").strip()

    selected_demo = DEMOS.get(choice)

    if selected_demo is None:
        print("Invalid choice")
        return

    _, run_demo = selected_demo

    print("\nRunning demo...\n")
    run_demo()


if __name__ == "__main__":
    main()
