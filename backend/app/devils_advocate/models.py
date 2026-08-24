from dataclasses import dataclass, field
from typing import List


@dataclass
class ChallengeResult:
    claim_id: int
    challenge: str
    status: str
    score: float
    explanation: str
    evidence_pages: List[int] = field(
        default_factory=list
    )


@dataclass
class DevilAdvocateReport:
    results: List[ChallengeResult] = field(
        default_factory=list
    )

    @property
    def overall_score(self) -> float:
        if not self.results:
            return 0.0

        return round(
            sum(
                result.score
                for result in self.results
            ) / len(self.results),
            3,
        )