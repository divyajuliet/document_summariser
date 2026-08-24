from dataclasses import dataclass

from backend.app.extraction.models import ExtractedDocument


@dataclass
class ExtractionQuality:
    score: float
    total_characters: int
    pages_with_text: int
    total_pages: int
    requires_fallback: bool
    reason: str

    # QEXT quality dimensions
    text_completeness: float
    page_coverage: float
    character_quality: float
    structural_consistency: float
    suspicious_character_score: float
    text_density: float


class ExtractionQualityEvaluator:

    MIN_CHARACTERS = 100
    MIN_PAGE_TEXT_RATIO = 0.20

    ACCEPT_THRESHOLD = 0.75

    # ==================================================
    # MAIN EVALUATION
    # ==================================================

    def evaluate(
        self,
        document: ExtractedDocument,
    ) -> ExtractionQuality:

        total_pages = document.total_pages
        total_characters = document.total_characters

        # --------------------------------------------------
        # EMPTY DOCUMENT
        # --------------------------------------------------

        if total_pages == 0:

            return ExtractionQuality(
                score=0.0,
                total_characters=0,
                pages_with_text=0,
                total_pages=0,
                requires_fallback=True,
                reason="Document contains no pages",

                text_completeness=0.0,
                page_coverage=0.0,
                character_quality=0.0,
                structural_consistency=0.0,
                suspicious_character_score=0.0,
                text_density=0.0,
            )

        # --------------------------------------------------
        # PAGE COVERAGE
        # --------------------------------------------------

        pages_with_text = sum(
            1
            for page in document.pages
            if page.char_count >= 20
        )

        page_text_ratio = (
            pages_with_text / total_pages
        )

        page_coverage = page_text_ratio

        # --------------------------------------------------
        # TEXT COMPLETENESS
        # --------------------------------------------------

        text_completeness = min(
            total_characters / 2000,
            1.0,
        )

        # --------------------------------------------------
        # CHARACTER QUALITY
        # --------------------------------------------------

        text = "\n".join(
            page.text
            for page in document.pages
        )

        if not text:

            character_quality = 0.0
            suspicious_character_score = 0.0

        else:

            valid_characters = sum(
                1
                for char in text
                if (
                    char.isalnum()
                    or char.isspace()
                    or char in ".,;:!?-()[]/%@'\""
                )
            )

            character_quality = (
                valid_characters / len(text)
            )

            suspicious_characters = sum(
                1
                for char in text
                if not (
                    char.isalnum()
                    or char.isspace()
                    or char in ".,;:!?-()[]/%@'\""
                )
            )

            suspicious_ratio = (
                suspicious_characters / len(text)
            )

            suspicious_character_score = max(
                0.0,
                min(
                    1.0,
                    1.0 - suspicious_ratio * 5,
                ),
            )

        # --------------------------------------------------
        # STRUCTURAL CONSISTENCY
        # --------------------------------------------------

        page_lengths = [
            page.char_count
            for page in document.pages
            if page.char_count > 0
        ]

        if not page_lengths:

            structural_consistency = 0.0

        elif len(page_lengths) == 1:

            structural_consistency = 1.0

        else:

            average = (
                sum(page_lengths)
                / len(page_lengths)
            )

            if average == 0:

                structural_consistency = 0.0

            else:

                deviations = [
                    abs(length - average)
                    / average
                    for length in page_lengths
                ]

                average_deviation = (
                    sum(deviations)
                    / len(deviations)
                )

                structural_consistency = max(
                    0.0,
                    min(
                        1.0,
                        1.0 - average_deviation,
                    ),
                )

        # --------------------------------------------------
        # TEXT DENSITY
        # --------------------------------------------------

        average_characters_per_page = (
            total_characters / total_pages
        )

        text_density = min(
            average_characters_per_page / 1500,
            1.0,
        )

        # --------------------------------------------------
        # FINAL QEXT SCORE
        # --------------------------------------------------

        score = (
            text_completeness * 0.25
            + page_coverage * 0.20
            + character_quality * 0.15
            + structural_consistency * 0.15
            + suspicious_character_score * 0.10
            + text_density * 0.15
        )

        score = round(
            min(max(score, 0.0), 1.0),
            3,
        )

        # --------------------------------------------------
        # FALLBACK DECISION
        # --------------------------------------------------

        requires_fallback = (
            total_characters < self.MIN_CHARACTERS
            or page_text_ratio < self.MIN_PAGE_TEXT_RATIO
            or score < self.ACCEPT_THRESHOLD
        )

        # --------------------------------------------------
        # REASON
        # --------------------------------------------------

        if total_characters == 0:

            reason = "No text extracted"

        elif page_text_ratio < self.MIN_PAGE_TEXT_RATIO:

            reason = (
                "Too few pages contain usable text"
            )

        elif total_characters < self.MIN_CHARACTERS:

            reason = "Too little text extracted"

        elif score < self.ACCEPT_THRESHOLD:

            reason = (
                "Extraction quality is borderline"
            )

        else:

            reason = "Extraction quality acceptable"

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        return ExtractionQuality(
            score=score,

            total_characters=total_characters,

            pages_with_text=pages_with_text,

            total_pages=total_pages,

            requires_fallback=requires_fallback,

            reason=reason,

            text_completeness=round(
                text_completeness,
                3,
            ),

            page_coverage=round(
                page_coverage,
                3,
            ),

            character_quality=round(
                character_quality,
                3,
            ),

            structural_consistency=round(
                structural_consistency,
                3,
            ),

            suspicious_character_score=round(
                suspicious_character_score,
                3,
            ),

            text_density=round(
                text_density,
                3,
            ),
        )