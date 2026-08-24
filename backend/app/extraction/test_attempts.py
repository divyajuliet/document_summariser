from backend.app.extraction.attempts import (
    ExtractionAttempt,
)


def main():

    attempt = ExtractionAttempt(
        attempt_number=1,
        method="pdf_text",
        quality_score=0.12,
        status="rejected",
        reason="No text extracted",
    )

    print()
    print("=" * 60)
    print("EXTRACTION ATTEMPT")
    print("=" * 60)

    print(attempt)

    print("=" * 60)


if __name__ == "__main__":
    main()