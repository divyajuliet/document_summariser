from pathlib import Path

from backend.app.extraction.pipeline import (
    ExtractionPipeline,
)

from backend.app.claims.extractor import (
    ClaimExtractor,
)


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("CLAIM EXTRACTION TEST")
    print("=" * 60)

    print()
    print(f"Testing: {TEST_FILE.name}")

    # --------------------------------------------------
    # EXTRACTION
    # --------------------------------------------------

    pipeline = ExtractionPipeline()

    document, attempts, validation = pipeline.extract(
        file_path=TEST_FILE,
        document_id="claim-test",
    )

    print()
    print("EXTRACTION")
    print("-" * 60)

    print(
        f"Pages: {document.total_pages}"
    )

    print(
        f"Characters: {document.total_characters}"
    )

    # --------------------------------------------------
    # CLAIM EXTRACTION
    # --------------------------------------------------

    extractor = ClaimExtractor()

    claims = extractor.extract(
        document
    )

    print()
    print("CLAIMS")
    print("-" * 60)

    print(
        f"Claims extracted: {len(claims)}"
    )

    # --------------------------------------------------
    # DISPLAY CLAIMS
    # --------------------------------------------------

    for claim in claims[:20]:

        print()
        print(
            f"Claim {claim.claim_id}"
        )

        print(
            f"Type: {claim.claim_type}"
        )

        print(
            f"Risk: {claim.risk}"
        )

        print(
            f"Confidence: {claim.confidence}"
        )

        print(
            f"Claim: {claim.claim_text}"
        )

        print(
            "Evidence:"
        )

        for evidence in claim.evidence:

            print(
                f"  Page {evidence.page_number}: "
                f"{evidence.text}"
            )

        if claim.entities:

            print(
                "Entities:",
                ", ".join(
                    entity.text
                    for entity in claim.entities
                )
            )

        if claim.numbers:

            print(
                "Numbers:",
                ", ".join(
                    number.text
                    for number in claim.numbers
                )
            )

        if claim.temporal_values:

            print(
                "Temporal:",
                ", ".join(
                    value.text
                    for value in claim.temporal_values
                )
            )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()