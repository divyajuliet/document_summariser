from backend.app.extraction.models import (
    ExtractedDocument,
)

from backend.app.validation.models import (
    ValidationQuestion,
    ValidationResult,
)


class ExtractionValidator:

    MIN_PAGE_CHARACTERS = 20
    MIN_DOCUMENT_CHARACTERS = 50

    def validate(
        self,
        document: ExtractedDocument,
    ) -> ValidationResult:

        questions = []

        # --------------------------------------------------
        # QUESTION 1: DOES THE DOCUMENT CONTAIN TEXT?
        # --------------------------------------------------

        has_text = (
            document.total_characters
            >= self.MIN_DOCUMENT_CHARACTERS
        )

        questions.append(
            ValidationQuestion(
                question=(
                    "Does the extraction contain "
                    "meaningful text?"
                ),
                passed=has_text,
                score=1.0 if has_text else 0.0,
                explanation=(
                    f"Extracted "
                    f"{document.total_characters} "
                    f"characters."
                ),
            )
        )

        # --------------------------------------------------
        # QUESTION 2: DID PAGES PRODUCE CONTENT?
        # --------------------------------------------------

        if document.total_pages > 0:

            pages_with_text = sum(
                1
                for page in document.pages
                if page.char_count
                >= self.MIN_PAGE_CHARACTERS
            )

            page_coverage = (
                pages_with_text
                / document.total_pages
            )

        else:

            page_coverage = 0.0

        questions.append(
            ValidationQuestion(
                question=(
                    "Did the extraction produce "
                    "meaningful content across pages?"
                ),
                passed=page_coverage >= 0.5,
                score=page_coverage,
                explanation=(
                    f"{pages_with_text if document.total_pages else 0}"
                    f"/{document.total_pages} pages contain "
                    f"meaningful text."
                ),
            )
        )

        # --------------------------------------------------
        # QUESTION 3: ARE THERE SUSPICIOUS OCR SYMBOLS?
        # --------------------------------------------------

        full_text = "\n".join(
            page.text
            for page in document.pages
        )

        suspicious_symbols = sum(
            1
            for char in full_text
            if char in "�¤§¶¦"
        )

        total_chars = max(
            len(full_text),
            1,
        )

        suspicious_ratio = (
            suspicious_symbols
            / total_chars
        )

        symbol_check_passed = (
            suspicious_ratio < 0.02
        )

        questions.append(
            ValidationQuestion(
                question=(
                    "Does the extraction avoid "
                    "excessive suspicious characters?"
                ),
                passed=symbol_check_passed,
                score=max(
                    0.0,
                    1.0 - suspicious_ratio * 10,
                ),
                explanation=(
                    f"Suspicious character ratio: "
                    f"{suspicious_ratio:.2%}."
                ),
            )
        )

        # --------------------------------------------------
        # QUESTION 4: IS THE EXTRACTION CONSISTENT?
        # --------------------------------------------------

        non_empty_pages = [
            page
            for page in document.pages
            if page.text.strip()
        ]

        consistency_passed = (
            len(non_empty_pages)
            > 0
        )

        questions.append(
            ValidationQuestion(
                question=(
                    "Does the extraction contain "
                    "consistent non-empty page content?"
                ),
                passed=consistency_passed,
                score=(
                    1.0
                    if consistency_passed
                    else 0.0
                ),
                explanation=(
                    f"{len(non_empty_pages)} "
                    f"non-empty pages detected."
                ),
            )
        )

        # --------------------------------------------------
        # OVERALL SCORE
        # --------------------------------------------------

        overall_score = (
            sum(
                question.score
                for question in questions
            )
            / len(questions)
        )

        # --------------------------------------------------
        # FINAL DECISION
        # --------------------------------------------------

        failed_questions = sum(
            1
            for question in questions
            if not question.passed
        )

        if (
            overall_score >= 0.75
            and failed_questions == 0
        ):

            decision = "accept"

        elif overall_score >= 0.45:

            decision = "review"

        else:

            decision = "reject"

        return ValidationResult(
            overall_score=round(
                overall_score,
                3,
            ),
            decision=decision,
            questions=questions,
        )