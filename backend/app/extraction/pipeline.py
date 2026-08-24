from pathlib import Path
from typing import List, Tuple

from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)
from backend.app.extraction.attempts import ExtractionAttempt
from backend.app.extraction.pdf_extractor import PDFExtractor
from backend.app.extraction.ocr_extractor import OCRExtractor
from backend.app.extraction.quality import ExtractionQualityEvaluator
from backend.app.validation.validator import ExtractionValidator


class ExtractionPipeline:

    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.ocr_extractor = OCRExtractor()
        self.quality_evaluator = ExtractionQualityEvaluator()
        self.validator = ExtractionValidator()

    def extract(
        self,
        file_path: Path,
        document_id: str,
    ) -> Tuple[ExtractedDocument, List[ExtractionAttempt]]:

        attempts = []

        # ==================================================
        # ATTEMPT 1 — PDF TEXT EXTRACTION
        # ==================================================

        try:
            pdf_document = self.pdf_extractor.extract(
                file_path=file_path,
                document_id=document_id,
            )

            pdf_quality = self.quality_evaluator.evaluate(
                pdf_document
            )

            pdf_validation = self.validator.validate(
                pdf_document
            )

            attempts.append(
                ExtractionAttempt(
                    attempt_number=1,
                    method="pdf_text",
                    quality_score=pdf_quality.score,
                    status=(
                        "accepted"
                        if pdf_validation.decision == "accept"
                        and not pdf_quality.requires_fallback
                        else "rejected"
                    ),
                    reason=pdf_quality.reason,
                )
            )

        except Exception as exc:

            pdf_document = None
            pdf_quality = None
            pdf_validation = None

            attempts.append(
                ExtractionAttempt(
                    attempt_number=1,
                    method="pdf_text",
                    quality_score=0.0,
                    status="failed",
                    reason="PDF text extraction failed",
                    error=str(exc),
                )
            )

        # ==================================================
        # ATTEMPT 2 — OCR EXTRACTION
        # ==================================================

        try:
            ocr_result = self.ocr_extractor.extract_pdf(
                file_path=file_path,
            )

            # OCR extractor currently returns a list of
            # strings. Convert each string into PageContent.
            ocr_pages = []

            for index, text in enumerate(ocr_result, start=1):

                # Make sure the value is a string.
                text = str(text)

                ocr_pages.append(
                    PageContent(
                        page_number=index,
                        text=text,
                        char_count=len(text),
                    )
                )

            ocr_document = ExtractedDocument(
                document_id=document_id,
                extraction_method="pdf_ocr",
                pages=ocr_pages,
            )

            ocr_quality = self.quality_evaluator.evaluate(
                ocr_document
            )

            ocr_validation = self.validator.validate(
                ocr_document
            )

            attempts.append(
                ExtractionAttempt(
                    attempt_number=2,
                    method="pdf_ocr",
                    quality_score=ocr_quality.score,
                    status=(
                        "accepted"
                        if ocr_validation.decision == "accept"
                        and not ocr_quality.requires_fallback
                        else "rejected"
                    ),
                    reason=ocr_quality.reason,
                )
            )

        except Exception as exc:

            ocr_document = None
            ocr_quality = None
            ocr_validation = None

            attempts.append(
                ExtractionAttempt(
                    attempt_number=2,
                    method="pdf_ocr",
                    quality_score=0.0,
                    status="failed",
                    reason="OCR extraction failed",
                    error=str(exc),
                )
            )

        # ==================================================
        # BUILD CANDIDATES
        # ==================================================

        candidates = []

        if (
            pdf_document is not None
            and pdf_quality is not None
            and pdf_validation is not None
        ):
            candidates.append(
                (
                    pdf_document,
                    pdf_quality,
                    pdf_validation,
                    "pdf_text",
                )
            )

        if (
            ocr_document is not None
            and ocr_quality is not None
            and ocr_validation is not None
        ):
            candidates.append(
                (
                    ocr_document,
                    ocr_quality,
                    ocr_validation,
                    "pdf_ocr",
                )
            )

        # ==================================================
        # MAKE SURE AT LEAST ONE EXTRACTION WORKED
        # ==================================================

        if not candidates:
            raise RuntimeError(
                "All extraction methods failed."
            )

        # ==================================================
        # PREFER VALIDATED EXTRACTIONS
        # ==================================================

        valid_candidates = [
            candidate
            for candidate in candidates
            if candidate[2].decision == "accept"
        ]

        if valid_candidates:
            candidates = valid_candidates

        # ==================================================
        # QEXT — HIGHEST QUALITY SCORE WINS
        # ==================================================

        (
            best_document,
            best_quality,
            best_validation,
            best_method,
        ) = max(
            candidates,
            key=lambda candidate: candidate[1].score,
        )

        # ==================================================
        # UPDATE FINAL STATUS
        # ==================================================

        for attempt in attempts:

            if attempt.method == best_method:

                attempt.status = "accepted"

                attempt.reason = (
                    f"Selected by QEXT with score "
                    f"{best_quality.score}"
                )

            elif attempt.status != "failed":

                attempt.status = "rejected"

        return best_document, attempts