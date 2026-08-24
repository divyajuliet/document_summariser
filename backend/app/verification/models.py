from dataclasses import dataclass, field
from typing import List


@dataclass
class VerificationResult:
    claim_id: int
    claim_text: str
    verification_status: str
    verification_score: float
    explanation: str
    evidence_pages: List[int] = field(
        default_factory=list
    )


@dataclass
class VerificationReport:
    claim_id: int
    results: List[VerificationResult] = field(
        default_factory=list
    )

    @property
    def overall_score(self) -> float:

        if not self.results:
            return 0.0

        return round(
            sum(
                result.verification_score
                for result in self.results
            )
            / len(self.results),
            3,
        )