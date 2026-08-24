from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationQuestion:
    question: str
    passed: bool
    score: float
    explanation: str


@dataclass
class ValidationResult:
    overall_score: float
    decision: str
    questions: List[ValidationQuestion] = field(
        default_factory=list
    )

    @property
    def passed(self) -> bool:
        return self.decision == "accept"