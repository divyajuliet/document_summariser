from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.claims.extractor import ClaimExtractor
from backend.app.evidence.retriever import EvidenceRetriever


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("EVIDENCE RETRIEVAL TEST")
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
    print("Claims extracted:", len(claims))

    if not claims:
        print("No claims available.")
        return

    retriever = EvidenceRetriever()

    claim = claims[0]

    all_evidence = [
        evidence
        for claim_item in claims
        for evidence in claim_item.evidence
    ]

    result = retriever.retrieve(
        claim=claim,
        evidence=all_evidence,
        top_k=3,
    )

    print()
    print("CLAIM")
    print("-" * 60)
    print(claim.claim_text)

    print()
    print("RETRIEVED EVIDENCE")
    print("-" * 60)

    for index, item in enumerate(
        result.results,
        start=1,
    ):

        print(f"Evidence {index}")
        print(f"Page: {item.page_number}")
        print(
            f"Relevance: "
            f"{item.relevance_score}"
        )
        print(
            f"Text: "
            f"{item.evidence_text}"
        )
        print()


if __name__ == "__main__":
    main()