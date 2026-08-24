from dataclasses import dataclass, field
from typing import List


@dataclass
class EvidenceItem:
    page_number: int
    evidence_text: str
    relevance_score: float


@dataclass
class EvidenceRetrievalResult:
    claim_id: int
    results: List[EvidenceItem] = field(
        default_factory=list
    )