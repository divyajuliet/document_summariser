from pathlib import Path

from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)

from backend.app.extraction.pdf_extractor import (
    PDFExtractor,
)

from backend.app.extraction.ocr_extractor import (
    OCRExtractor,
)

from backend.app.extraction.quality import (
    ExtractionQualityEvaluator,
)

from backend.app.extraction.attempts import (
    ExtractionAttempt,
)


class ExtractionPipeline:

    FALLBACK_THRESHOLD = 0.20

    def __init__(self):

        self.pdf_extractor = PDFExtractor()
        self.ocr_extractor = OCRExtractor()
        self.quality_evaluator = (
            ExtractionQualityEvaluator()
        )

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ):

        extension = file_path.suffix.lower()

        attempts = []

        # --------------------------------------------------
        # IMAGE
        # --------------------------------------------------

        if extension in {
            ".png",
            ".jpg",
            ".jpeg",
        }:

            text = self.ocr_extractor.extract_image(
                file_path
            )

            document = ExtractedDocument(
                document_id=document_id,
                extraction_method="ocr",
                pages=[
                    PageContent(
                        page_number=1,
                        text=text,
                        char_count=len(text),
                    )
                ],
            )

            quality = (
                self.quality_evaluator.evaluate(
                    document
                )
            )

            attempts.append(
                ExtractionAttempt(
                    attempt_number=2,
                    method="pdf_ocr",
                    quality_score=ocr_quality.score,
                    status=(
                        "accepted"
                        if not ocr_quality.requires_fallback
                        else "rejected"
                    ),
                    reason=ocr_quality.reason,
                )
            )

            return document, attempts

        # --------------------------------------------------
        # PDF
        # --------------------------------------------------

        if extension == ".pdf":

            # ----------------------------------------------
            # ATTEMPT 1: NATIVE PDF EXTRACTION
            # ----------------------------------------------

            native_document = (
                self.pdf_extractor.extract(
                    file_path=file_path,
                    document_id=document_id,
                )
            )

            native_quality = (
                self.quality_evaluator.evaluate(
                    native_document
                )
            )

            attempts.append(
                ExtractionAttempt(
                    attempt_number=1,
                    method="pdf_text",
                    quality_score=native_quality.score,
                    status=(
                        "accepted"
                        if not native_quality.requires_fallback
                        else "rejected"
                    ),
                    reason=native_quality.reason,
                )
            )

            # ----------------------------------------------
            # GOOD ENOUGH → ACCEPT
            # ----------------------------------------------

            if not native_quality.requires_fallback:

                return (
                    native_document,
                    attempts,
                )

            # ----------------------------------------------
            # ATTEMPT 2: OCR FALLBACK
            # ----------------------------------------------

            ocr_pages = (
                self.ocr_extractor.extract_pdf(
                    file_path
                )
            )

            ocr_document = ExtractedDocument(
                document_id=document_id,
                extraction_method="pdf_ocr",
                pages=[
                    PageContent(
                        page_number=index,
                        text=text,
                        char_count=len(text),
                    )
                    for index, text in enumerate(
                        ocr_pages,
                        start=1,
                    )
                ],
            )

            ocr_quality = (
                self.quality_evaluator.evaluate(
                    ocr_document
                )
            )

            attempts.append(
                ExtractionAttempt(
                    attempt_number=2,
                    method="pdf_ocr",
                    quality_score=ocr_quality.score,
                    status="accepted",
                    reason=ocr_quality.reason,
                )
            )

            # ----------------------------------------------
            # COMPARE EXTRACTIONS
            # ----------------------------------------------

            # --------------------------------------------------
# SELECT BEST EXTRACTION
# --------------------------------------------------

        if ocr_quality.score > native_quality.score:
            return (
                ocr_document,
                attempts,
            )
        return (
            native_document,
            attempts,
        )