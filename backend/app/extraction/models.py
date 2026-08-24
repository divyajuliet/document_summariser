from dataclasses import dataclass, field
from typing import List


@dataclass
class PageContent:
    page_number: int
    text: str
    char_count: int


@dataclass
class ExtractedDocument:
    document_id: str
    extraction_method: str
    pages: List[PageContent] = field(default_factory=list)

    @property
    def total_pages(self) -> int:
        return len(self.pages)

    @property
    def total_characters(self) -> int:
        return sum(page.char_count for page in self.pages)