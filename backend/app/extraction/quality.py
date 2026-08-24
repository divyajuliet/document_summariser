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


class ExtractionQualityEvaluator:

    MIN_CHARACTERS = 100
    MIN_PAGE_TEXT_RATIO = 0.20

    def evaluate(
        self,
        document: ExtractedDocument,
    ) -> ExtractionQuality:

        total_pages = document.total_pages
        total_characters = document.total_characters

        if total_pages == 0:

            return ExtractionQuality(
                score=0.0,
                total_characters=0,
                pages_with_text=0,
                total_pages=0,
                requires_fallback=True,
                reason="Document contains no pages",
            )

        pages_with_text = sum(
            1
            for page in document.pages
            if page.char_count >= 20
        )

        page_text_ratio = (
            pages_with_text / total_pages
        )

        # Character score.
        # 1000+ characters gives the maximum score.
        character_score = min(
            total_characters / 1000,
            1.0,
        )

        # Page coverage score.
        page_score = page_text_ratio

        # Combined quality score.
        score = (
            0.5 * character_score
            + 0.5 * page_score
        )

        requires_fallback = (
            total_characters < self.MIN_CHARACTERS
            or page_text_ratio < self.MIN_PAGE_TEXT_RATIO
        )

        if total_characters == 0:
            reason = "No text extracted"

        elif page_text_ratio < self.MIN_PAGE_TEXT_RATIO:
            reason = "Too few pages contain usable text"

        elif total_characters < self.MIN_CHARACTERS:
            reason = "Too little text extracted"

        else:
            reason = "Extraction quality acceptable"

        return ExtractionQuality(
            score=round(score, 3),
            total_characters=total_characters,
            pages_with_text=pages_with_text,
            total_pages=total_pages,
            requires_fallback=requires_fallback,
            reason=reason,
        )