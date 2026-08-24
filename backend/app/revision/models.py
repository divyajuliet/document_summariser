from dataclasses import dataclass, field
from typing import List


@dataclass
class VerificationScore:
    factuality: float = 0.0
    evidence_coverage: float = 0.0
    consistency: float = 0.0
    completeness: float = 0.0
    numerical_consistency: float = 0.0
    contradiction_penalty: float = 0.0

    @property
    def overall_score(self) -> float:
        score = (
            self.factuality
            + self.evidence_coverage
            + self.consistency
            + self.completeness
            + self.numerical_consistency
        ) / 5.0

        score -= self.contradiction_penalty

        return round(
            max(0.0, min(1.0, score)),
            3,
        )


@dataclass
class SummaryRevision:
    version: int
    summary: str
    verification_score: float
    status: str
    reason: str


@dataclass
class RevisionHistory:
    revisions: List[SummaryRevision] = field(
        default_factory=list
    )

    best_version: int = 0

    @property
    def best_score(self) -> float:

        if not self.revisions:
            return 0.0

        return max(
            revision.verification_score
            for revision in self.revisions
        )