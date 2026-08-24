from dataclasses import dataclass, field
from typing import List


@dataclass
class Entity:
    text: str
    entity_type: str


@dataclass
class NumberValue:
    text: str
    value: float | None = None
    unit: str | None = None


@dataclass
class TemporalValue:
    text: str


@dataclass
class Evidence:
    page_number: int
    text: str


@dataclass
class Claim:
    claim_id: int
    claim_text: str
    claim_type: str

    entities: List[Entity] = field(
        default_factory=list
    )

    numbers: List[NumberValue] = field(
        default_factory=list
    )

    temporal_values: List[TemporalValue] = field(
        default_factory=list
    )

    evidence: List[Evidence] = field(
        default_factory=list
    )

    confidence: float = 0.0
    risk: str = "LOW"