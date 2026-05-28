from datetime import timedelta

# Transfer fee rate applied to the sender
TRANSFER_FEE_RATE: float = 0.01

# Supported exchange rates keyed by (from_currency, to_currency)
EXCHANGE_RATES: dict[tuple[str, str], float] = {
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.08,
    ("USD", "RUB"): 90.0,
    ("RUB", "USD"): 0.011,
    ("USD", "KZT"): 450.0,
    ("KZT", "USD"): 0.0022,
    ("EUR", "RUB"): 98.0,
    ("RUB", "EUR"): 0.010,
}

# Risk analysis thresholds
RISK_HIGH_AMOUNT: float = 10_000.0
RISK_MEDIUM_AMOUNT: float = 5_000.0
RISK_FREQUENT_LIMIT: int = 5
RISK_FREQUENT_WINDOW: timedelta = timedelta(minutes=1)

# Night hours during which bank operations are restricted [start, end)
NIGHT_HOUR_START: int = 0
NIGHT_HOUR_END: int = 5

# Authentication limits
SUSPICIOUS_LOGIN_ATTEMPTS: int = 2
MAX_FAILED_LOGIN_ATTEMPTS: int = 3
