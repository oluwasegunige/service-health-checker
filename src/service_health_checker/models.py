from dataclasses import dataclass
from typing import Any

@dataclass
class CheckResult:
    check_type: str
    success: bool
    duration: float
    details: dict[str, Any] | None = None
    error: str | None = None
