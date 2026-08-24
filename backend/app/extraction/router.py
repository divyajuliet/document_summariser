from pathlib import Path

from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)
from backend.app.extraction.pdf_extractor import PDFExtractor
from backend.app.extraction.ocr_extractor import OCRExtractor


class ExtractionRouter:

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.ocr_extractor = OCRExtractor()

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> ExtractedDocument:

        extension = file_path.suffix.lower()

        # -----------------------------------------
        # PDF
        # -----------------------------------------

        if extension == ".pdf":

            return self.pdf_extractor.extract(
                file_path=file_path,
                document_id=document_id,
            )

        # -----------------------------------------
        # IMAGE → OCR
        # -----------------------------------------

        if extension in {".png", ".jpg", ".jpeg"}:

            text = self.ocr_extractor.extract_image(
                file_path=file_path,
            )

            page = PageContent(
                page_number=1,
                text=text,
                char_count=len(text),
            )

            return ExtractedDocument(
                document_id=document_id,
                extraction_method="ocr",
                pages=[page],
            )

        # -----------------------------------------
        # UNSUPPORTED FORMAT
        # -----------------------------------------

        raise ValueError(
            f"No extraction strategy available "
            f"for file type: {extension}"
        )