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

### Transactions
- transaction model
- transaction queue
- priority handling
- delayed transactions
- transaction cancellation
- transaction processor
- fees for transfers
- simple currency conversion
- failed transaction tracking

### Audit and Risk Analysis
- audit logging
- log filtering
- save audit logs to file
- transaction risk analysis
- suspicious transaction detection
- client risk profiles
- error statistics

### Full System Simulation
- demo setup with 7 clients
- 14 bank accounts
- 30+ simulated transactions
- successful, failed, cancelled and delayed transactions
- user scenarios
- transaction history overview
- suspicious activity overview
- final summary reports

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
- Day 4 — Transactions, queue and processing
- Day 5 — Audit and risk analysis
- Day 6 — Full banking system simulation
