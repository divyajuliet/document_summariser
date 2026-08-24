from pathlib import Path
from typing import Any, Dict

from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)
from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.extraction.ocr_extractor import OCRExtractor


class ExtractionRouter:

    def __init__(self):
        self.pipeline = ExtractionPipeline()
        self.ocr_extractor = OCRExtractor()

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> Dict[str, Any]:

        extension = file_path.suffix.lower()

        # ============================================================
        # PDF → QEXT EXTRACTION PIPELINE
        # ============================================================

        if extension == ".pdf":

            document, attempts, validation = (
                self.pipeline.extract(
                    file_path=file_path,
                    document_id=document_id,
                )
            )

            return {
                "document": document,
                "attempts": attempts,
                "validation": validation,
            }

        # ============================================================
        # IMAGE → OCR
        # ============================================================

        if extension in {".png", ".jpg", ".jpeg"}:

            text = self.ocr_extractor.extract_image(
                file_path=file_path,
            )

            page = PageContent(
                page_number=1,
                text=text,
                char_count=len(text),
            )

            document = ExtractedDocument(
                document_id=document_id,
                extraction_method="ocr",
                pages=[page],
            )

            return {
                "document": document,
                "attempts": [],
                "validation": None,
            }

        # ============================================================
        # UNSUPPORTED FORMAT
        # ============================================================

        raise ValueError(
            f"No extraction strategy available "
            f"for file type: {extension}"
        )