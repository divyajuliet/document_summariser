from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline


def main():

    # Change this filename if you want to test another PDF.
    file_path = Path(
        "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
    )

    document_id = "24d5655e-d67d-444e-9896-567cde443fc3"

    pipeline = ExtractionPipeline()

    print()
    print("=" * 60)
    print("EXTRACTION PIPELINE TEST")
    print("=" * 60)

    document, attempts = pipeline.extract(
        file_path=file_path,
        document_id=document_id,
    )

    # ==================================================
    # FINAL EXTRACTION
    # ==================================================

    print()
    print("FINAL EXTRACTION")
    print("-" * 60)

    print(f"Method: {document.extraction_method}")
    print(f"Pages: {document.total_pages}")
    print(f"Characters: {document.total_characters}")

    # ==================================================
    # FINAL VALIDATION
    # ==================================================

    from backend.app.validation.validator import ExtractionValidator

    validator = ExtractionValidator()

    validation = validator.validate(document)

    print(f"Validation score: {validation.overall_score}")
    print(f"Validation decision: {validation.decision}")

    # ==================================================
    # ATTEMPTS
    # ==================================================

    print()
    print("ATTEMPTS")
    print("-" * 60)

    for attempt in attempts:

        print(
            f"Attempt {attempt.attempt_number}: "
            f"{attempt.method}"
        )

        print(
            f"Quality Score: "
            f"{attempt.quality_score}"
        )

        print(
            f"Status: "
            f"{attempt.status}"
        )

        print(
            f"Reason: "
            f"{attempt.reason}"
        )

        if attempt.error:
            print(
                f"Error: "
                f"{attempt.error}"
            )

        print()

    print("=" * 60)


if __name__ == "__main__":
    main()