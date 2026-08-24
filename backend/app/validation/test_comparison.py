from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)

from backend.app.validation.models import (
    ValidationResult,
)

from backend.app.validation.comparison import (
    ExtractionComparator,
)


def create_document(
    method: str,
    text: str,
) -> ExtractedDocument:

    return ExtractedDocument(
        document_id="comparison-test",
        extraction_method=method,
        pages=[
            PageContent(
                page_number=1,
                text=text,
                char_count=len(text),
            )
        ],
    )


def main():

    # --------------------------------------------------
    # SIMULATED NATIVE EXTRACTION
    # --------------------------------------------------

    native = create_document(
        "pdf_text",
        (
            "This document contains "
            "information about machine "
            "learning and document extraction."
        ),
    )

    # --------------------------------------------------
    # SIMULATED OCR EXTRACTION
    # --------------------------------------------------

    ocr = create_document(
        "pdf_ocr",
        (
            "This document contains "
            "information about machine "
            "learning and document extraction."
        ),
    )

    # --------------------------------------------------
    # VALIDATION RESULTS
    # --------------------------------------------------

    native_validation = ValidationResult(
        overall_score=1.0,
        decision="accept",
    )

    ocr_validation = ValidationResult(
        overall_score=0.9,
        decision="accept",
    )

    # --------------------------------------------------
    # COMPARE
    # --------------------------------------------------

    comparator = ExtractionComparator()

    result = comparator.compare(
        first_document=native,
        first_quality=0.95,
        first_validation=native_validation,
        second_document=ocr,
        second_quality=0.80,
        second_validation=ocr_validation,
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("CROSS-EXTRACTION COMPARISON TEST")
    print("=" * 60)

    print()

    print(
        f"Preferred method: "
        f"{result.preferred_method}"
    )

    print(
        f"Preferred score: "
        f"{result.preferred_score}"
    )

    print(
        f"Alternative score: "
        f"{result.alternative_score}"
    )

    print(
        f"Agreement score: "
        f"{result.agreement_score}"
    )

    print(
        f"Decision: "
        f"{result.decision}"
    )

    print(
        f"Reason: "
        f"{result.reason}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()