from pathlib import Path

from backend.app.extraction.pipeline import (
    ExtractionPipeline,
)


PDF_PATH = Path(
    "uploads/scanned_test.pdf"
)


def main():

    if not PDF_PATH.exists():

        print(
            f"PDF not found: {PDF_PATH}"
        )

        return

    print()
    print("=" * 60)
    print("EXTRACTION PIPELINE TEST")
    print("=" * 60)

    pipeline = ExtractionPipeline()

    document, attempts = pipeline.extract(
        file_path=PDF_PATH,
        document_id="pipeline-test",
    )

    print()
    print("FINAL EXTRACTION")
    print("-" * 60)

    print(
        f"Method: "
        f"{document.extraction_method}"
    )

    print(
        f"Pages: "
        f"{document.total_pages}"
    )

    print(
        f"Characters: "
        f"{document.total_characters}"
    )

    print()
    print("ATTEMPTS")
    print("-" * 60)

    for attempt in attempts:

        print(
            f"Attempt {attempt.attempt_number}: "
            f"{attempt.method}"
        )

        print(
            f"Score: "
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

        print()

    print("=" * 60)


if __name__ == "__main__":
    main()