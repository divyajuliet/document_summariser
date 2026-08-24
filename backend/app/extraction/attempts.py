from dataclasses import dataclass
from typing import Optional


@dataclass
class ExtractionAttempt:

    attempt_number: int

    method: str

    quality_score: float

    status: str

    reason: str

    error: Optional[str] = None