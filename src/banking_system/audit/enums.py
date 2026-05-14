from enum import Enum


class AuditLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RiskLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
