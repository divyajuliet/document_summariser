from dataclasses import dataclass, field
from typing import List


@dataclass
class SummaryResult:
    document_id: str
    summary: str
    source_characters: int
    summary_characters: int
    chunks_processed: int
    method: str
