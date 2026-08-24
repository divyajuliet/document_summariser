from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline


def main():

    print()
    print("=" * 60)
    print("EXTRACTION PIPELINE TEST")
    print("=" * 60)

    # ------------------------------------------------------------
    # CHANGE THIS FILE NAME IF YOU WANT TO TEST A DIFFERENT PDF
    # ------------------------------------------------------------

    file_path = Path(
        "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
    )

    document_id = "test-document"

    # ------------------------------------------------------------
    # CREATE PIPELINE
    # ------------------------------------------------------------

    pipeline = ExtractionPipeline()

    # ------------------------------------------------------------
    # RUN EXTRACTION
    # ------------------------------------------------------------

    document, attempts, validation = pipeline.extract(
        file_path=file_path,
        document_id=document_id,
    )

    # ------------------------------------------------------------
    # FINAL EXTRACTION
    # ------------------------------------------------------------

    print()
    print("FINAL EXTRACTION")
    print("-" * 60)

    print(
        f"Method: {document.extraction_method}"
    )

    print(
        f"Pages: {document.total_pages}"
    )

    print(
        f"Characters: {document.total_characters}"
    )

    # ------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------

    print()
    print("VALIDATION")
    print("-" * 60)

    print(
        f"Validation Score: "
        f"{validation.overall_score}"
    )

    print(
        f"Validation Decision: "
        f"{validation.decision}"
    )

    # ------------------------------------------------------------
    # ATTEMPTS
    # ------------------------------------------------------------

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