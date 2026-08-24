from dataclasses import dataclass, field
from typing import List


@dataclass
class VerificationQuestion:
    question_id: int
    claim_id: int
    question: str
    question_type: str
    priority: str


@dataclass
class QuestionGenerationResult:
    questions: List[VerificationQuestion] = field(
        default_factory=list
    )