from dataclasses import dataclass
from typing import List

from backend.app.extraction.models import ExtractedDocument


@dataclass
class DocumentChunk:
    chunk_id: int
    page_start: int
    page_end: int
    text: str
    character_count: int


class DocumentChunker:

    MAX_CHARS = 4000
    OVERLAP_CHARS = 300

    def chunk(
        self,
        document: ExtractedDocument,
    ) -> List[DocumentChunk]:

        chunks = []
        chunk_id = 1

        current_text = ""
        current_page_start = None
        current_page_end = None

        for page in document.pages:

            page_text = page.text.strip()

            if not page_text:
                continue

            if current_page_start is None:
                current_page_start = page.page_number

            # If adding this page would exceed the limit,
            # save the current chunk first.
            if (
                current_text
                and len(current_text) + len(page_text) + 2
                > self.MAX_CHARS
            ):

                chunks.append(
                    DocumentChunk(
                        chunk_id=chunk_id,
                        page_start=current_page_start,
                        page_end=current_page_end,
                        text=current_text.strip(),
                        character_count=len(
                            current_text.strip()
                        ),
                    )
                )

                chunk_id += 1

                # Keep a small overlap from the previous
                # chunk to preserve context.
                overlap = current_text[
                    -self.OVERLAP_CHARS:
                ]

                current_text = overlap + "\n\n"
                current_page_start = current_page_end

            current_text += page_text + "\n\n"
            current_page_end = page.page_number

        # Add final chunk.
        if current_text.strip():

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    page_start=current_page_start,
                    page_end=current_page_end,
                    text=current_text.strip(),
                    character_count=len(
                        current_text.strip()
                    ),
                )
            )

        return chunks
