from pathlib import Path

import pymupdf
from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)


class PDFExtractor:

    def extract(
        self,
        file_path: Path,
        document_id: str
    ) -> ExtractedDocument:

        pages = []

        pdf = pymupdf.open(file_path)

        try:
            for page_index, page in enumerate(pdf):

                text = page.get_text("text")

                text = self._normalize_text(text)

                pages.append(
                    PageContent(
                        page_number=page_index + 1,
                        text=text,
                        char_count=len(text),
                    )
                )

        finally:
            pdf.close()

        return ExtractedDocument(
            document_id=document_id,
            extraction_method="pdf_text",
            pages=pages,
        )

    @staticmethod
    def _normalize_text(text: str) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)