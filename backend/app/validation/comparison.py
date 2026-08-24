from dataclasses import dataclass
from typing import Optional

from backend.app.extraction.models import ExtractedDocument
from backend.app.validation.models import ValidationResult


@dataclass
class ComparisonResult:
    preferred_method: str
    preferred_document: ExtractedDocument

    preferred_score: float
    alternative_score: Optional[float]

    agreement_score: float

    decision: str
    reason: str


class ExtractionComparator:

    # --------------------------------------------------
    # WEIGHTS
    # --------------------------------------------------

    QUALITY_WEIGHT = 0.50
    VALIDATION_WEIGHT = 0.30
    CONTENT_WEIGHT = 0.20

    # --------------------------------------------------
    # CALCULATE CONTENT SCORE
    # --------------------------------------------------

    @staticmethod
    def content_score(
        document: ExtractedDocument,
    ) -> float:

        if document.total_characters == 0:
            return 0.0

        meaningful_pages = sum(
            1
            for page in document.pages
            if page.char_count >= 20
        )

        if document.total_pages == 0:
            return 0.0

        return (
            meaningful_pages
            / document.total_pages
        )

    # --------------------------------------------------
    # CALCULATE COMBINED SCORE
    # --------------------------------------------------

    def calculate_score(
        self,
        document: ExtractedDocument,
        quality_score: float,
        validation: ValidationResult,
    ) -> float:

        content = self.content_score(
            document
        )

        score = (
            quality_score
            * self.QUALITY_WEIGHT
            +
            validation.overall_score
            * self.VALIDATION_WEIGHT
            +
            content
            * self.CONTENT_WEIGHT
        )

        return round(
            score,
            3,
        )

    # --------------------------------------------------
    # COMPARE TWO EXTRACTIONS
    # --------------------------------------------------

    def compare(
        self,
        first_document: ExtractedDocument,
        first_quality: float,
        first_validation: ValidationResult,
        second_document: ExtractedDocument,
        second_quality: float,
        second_validation: ValidationResult,
    ) -> ComparisonResult:

        first_score = self.calculate_score(
            first_document,
            first_quality,
            first_validation,
        )

        second_score = self.calculate_score(
            second_document,
            second_quality,
            second_validation,
        )

        # ----------------------------------------------
        # AGREEMENT
        # ----------------------------------------------

        agreement = self._calculate_agreement(
            first_document,
            second_document,
        )

        # ----------------------------------------------
        # SELECT PREFERRED RESULT
        # ----------------------------------------------

        if first_score >= second_score:

            preferred_document = (
                first_document
            )

            preferred_method = (
                first_document.extraction_method
            )

            preferred_score = first_score
            alternative_score = second_score

        else:

            preferred_document = (
                second_document
            )

            preferred_method = (
                second_document.extraction_method
            )

            preferred_score = second_score
            alternative_score = first_score

        # ----------------------------------------------
        # DECISION
        # ----------------------------------------------

        score_difference = abs(
            first_score
            - second_score
        )

        if (
            score_difference < 0.10
            and agreement >= 0.70
        ):

            decision = "stable"

            reason = (
                "Extraction methods have "
                "similar scores and strong "
                "content agreement."
            )

        elif (
            score_difference >= 0.20
        ):

            decision = "clear_winner"

            reason = (
                "One extraction method "
                "significantly outperformed "
                "the other."
            )

        elif agreement < 0.40:

            decision = "conflict"

            reason = (
                "Extraction methods show "
                "significant content disagreement."
            )

        else:

            decision = "preferred"

            reason = (
                "One extraction method is "
                "preferred, but the difference "
                "is not substantial."
            )

        return ComparisonResult(
            preferred_method=preferred_method,
            preferred_document=preferred_document,
            preferred_score=preferred_score,
            alternative_score=alternative_score,
            agreement_score=round(
                agreement,
                3,
            ),
            decision=decision,
            reason=reason,
        )

    # --------------------------------------------------
    # SIMPLE CONTENT AGREEMENT
    # --------------------------------------------------

    @staticmethod
    def _calculate_agreement(
        first: ExtractedDocument,
        second: ExtractedDocument,
    ) -> float:

        first_text = "\n".join(
            page.text.lower().strip()
            for page in first.pages
        )

        second_text = "\n".join(
            page.text.lower().strip()
            for page in second.pages
        )

        if not first_text or not second_text:
            return 0.0

        first_words = set(
            first_text.split()
        )

        second_words = set(
            second_text.split()
        )

        if not first_words or not second_words:
            return 0.0

        intersection = (
            first_words
            & second_words
        )

        union = (
            first_words
            | second_words
        )

        if not union:
            return 0.0

        return (
            len(intersection)
            / len(union)
        )