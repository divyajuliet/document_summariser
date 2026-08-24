from pathlib import Path

from backend.app.extraction.pipeline import (
    ExtractionPipeline,
)

from backend.app.claims.extractor import (
    ClaimExtractor,
)

from backend.app.evidence.retriever import (
    EvidenceRetriever,
)

from backend.app.verification.verifier import (
    ClaimVerifier,
)


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("VERIFICATION ENGINE TEST")
    print("=" * 60)

    # --------------------------------------------------
    # EXTRACTION
    # --------------------------------------------------

    pipeline = ExtractionPipeline()

    document, attempts, validation = (
        pipeline.extract(
            file_path=TEST_FILE,
            document_id="test-document",
        )
    )

    # --------------------------------------------------
    # CLAIM EXTRACTION
    # --------------------------------------------------

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

    # --------------------------------------------------
    # EVIDENCE RETRIEVAL
    # --------------------------------------------------

    retriever = EvidenceRetriever()

    claim = claims[0]

    all_evidence = [
        evidence
        for claim_item in claims
        for evidence in claim_item.evidence
    ]

    retrieval_result = (
        retriever.retrieve(
            claim=claim,
            evidence=all_evidence,
            top_k=3,
        )
    )

    retrieved_evidence = [
        EvidenceAdapter.to_claim_evidence(
            item
        )
        for item in retrieval_result.results
    ]

    # --------------------------------------------------
    # VERIFICATION
    # --------------------------------------------------

    verifier = ClaimVerifier()

    report = verifier.verify(
        claim=claim,
        evidence=retrieved_evidence,
    )

    print()
    print("CLAIM")
    print("-" * 60)
    print(claim.claim_text)

    print()
    print("VERIFICATION")
    print("-" * 60)

    for index, result in enumerate(
        report.results,
        start=1,
    ):

        print(
            f"Check {index}: "
            f"{result.verification_status}"
        )

        print(
            f"Score: "
            f"{result.verification_score}"
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

    print(
        "Overall verification score:",
        report.overall_score,
    )


class EvidenceAdapter:

    @staticmethod
    def to_claim_evidence(item):

        from backend.app.claims.models import (
            Evidence,
        )

        return Evidence(
            page_number=item.page_number,
            text=item.evidence_text,
        )


if __name__ == "__main__":
    main()