# Banking System

OOP banking system written in Python 3.11+.

The project demonstrates:
- abstract classes
- inheritance and polymorphism
- account management
- client management
- authentication and security checks
- account status handling
- transaction processing with queues and priorities
- audit logging and risk analysis
- reporting and visualization

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

### Reporting and Visualization
- bank reports
- client reports
- risk reports
- text report generation
- JSON export
- CSV export
- pie charts for transaction statuses
- bar charts for top clients
- line charts for client balance movement

## Project Structure

```text
.
├── main.py
├── README.md
├── requirements.txt
├── tests/
├── logs/
│   └── audit.log
├── reports/
│   ├── charts/      (PNG visualizations)
│   ├── csv/         (CSV exports)
│   └── json/        (JSON exports)
└── src/
    └── banking_system/
        ├── accounts/
        ├── audit/
        ├── bank/
        ├── clients/
        ├── demo/
        ├── exceptions/
        ├── reports/
        └── transactions/
```

## Requirements

- Python 3.11+
- matplotlib

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

From the project root:

```bash
PYTHONPATH=src python main.py
```

Then select a demo from the menu.

## Tests

```bash
PYTHONPATH=src python -m pytest tests/ -v
```

## Demo Days

- Day 1 — Basic bank accounts: deposit, withdraw, balance, status
- Day 2 — Advanced account types: savings interest, premium overdraft, investment portfolio
- Day 3 — Bank system and security: client registration, PIN auth, account lifecycle
- Day 4 — Transactions, queue and processing: priorities, delays, fees, currency conversion
- Day 5 — Audit and risk analysis: log levels, risk scoring, suspicious activity detection
- Day 6 — Full banking system simulation: 7 clients, 14 accounts, 30+ transactions end-to-end
- Day 7 — Reports and visualization: text reports, JSON/CSV export, pie/bar/line charts
