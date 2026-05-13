# Banking System

OOP banking system written in Python.

The project demonstrates:
- abstract classes
- inheritance and polymorphism
- account management
- client management
- authentication and security checks
- account status handling
- transaction-related architecture preparation

## Features

### Accounts
- BankAccount
- SavingsAccount
- PremiumAccount
- InvestmentAccount

### Client System
- client registration
- PIN authentication
- suspicious activity detection
- account ownership

### Bank System
- open / close / freeze accounts
- account search
- client ranking
- total balance calculation
- night operation restrictions

## Project Structure

```text
.
├── main.py
├── README.md
├── requirements.txt
└── src/
    └── banking_system/
        ├── accounts/
        ├── bank/
        ├── clients/
        ├── demo/
        └── exceptions/
```

## Requirements

- Python 3.11+

## Run Project

From the project root:

```bash
PYTHONPATH=src python main.py
```

Then select a demo from the menu.

## Demo Days

- Day 1 — Basic bank accounts
- Day 2 — Advanced account types
- Day 3 — Bank system and security

Additional functionality may be added in future iterations:
- transaction processing
- audit logging
- risk analysis
- reporting and visualization