from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.claims.extractor import ClaimExtractor
from backend.app.evidence.retriever import EvidenceRetriever
from backend.app.devils_advocate.checker import (
    DevilAdvocateChecker,
)


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("DEVIL'S ADVOCATE TEST")
    print("=" * 60)

    pipeline = ExtractionPipeline()

    document, attempts, validation = pipeline.extract(
        file_path=TEST_FILE,
        document_id="test-document",
    )

    extractor = ClaimExtractor()

    claims = extractor.extract(
        document=document,
    )

    print()
    print(
        "Claims extracted:",
        len(claims),
    )

    if not claims:
        print("No claims available.")
        return

    retriever = EvidenceRetriever()

    # Retrieve evidence for the highest-priority claims.
    prioritized_claims = sorted(
        claims,
        key=lambda claim: (
            claim.risk,
            -claim.confidence,
        ),
    )

    selected_claims = prioritized_claims[:10]

    all_evidence = []

    for claim in selected_claims:

        result = retriever.retrieve(
            claim=claim,
            evidence=[
                evidence
                for claim_item in claims
                for evidence in claim_item.evidence
            ],
            top_k=3,
        )

        all_evidence.extend(
            result.results
        )

    # Remove duplicate evidence.
    unique_evidence = []

    seen = set()

    for item in all_evidence:

        key = (
            item.page_number,
            item.evidence_text.strip(),
        )

        if key not in seen:

            seen.add(key)
            unique_evidence.append(item)

    print(
        "Unique evidence items:",
        len(unique_evidence),
    )

    checker = DevilAdvocateChecker()

    report = checker.check(
        claims=claims,
        evidence=unique_evidence,
    )

    print()
    print("CHALLENGE RESULTS")
    print("-" * 60)

    for index, result in enumerate(
        report.results,
        start=1,
    ):

        print(
            f"Challenge {index}"
        )

        print(
            f"Claim ID: "
            f"{result.claim_id}"
        )

        print(
            f"Challenge: "
            f"{result.challenge}"
        )

        print(
            f"Status: "
            f"{result.status}"
        )

        print(
            f"Score: "
            f"{result.score}"
        )

        print(
            f"Explanation: "
            f"{result.explanation}"
        )

        print(
            f"Evidence pages: "
            f"{result.evidence_pages}"
        )

        print()

    print("=" * 60)
    print("DEVIL'S ADVOCATE SCORE")
    print("=" * 60)

    print(
        "Overall score:",
        report.overall_score,
    )


if __name__ == "__main__":
    main()