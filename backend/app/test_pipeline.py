from pathlib import Path

from backend.app.pipeline import DocumentIntelligencePipeline


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("DOCUMENT INTELLIGENCE PIPELINE TEST")
    print("=" * 60)

    if not TEST_FILE.exists():
        print("Test file not found:", TEST_FILE)
        return

    pipeline = DocumentIntelligencePipeline()

    result = pipeline.process(
        file_path=TEST_FILE,
        document_id="test-document",
    )

    document = result["document"]
    claims = result["claims"]
    summary = result["summary"]
    questions = result["questions"]
    verification_score = result["verification_score"]
    devil_report = result["devils_advocate"]
    revision = result["revision"]

    print()
    print("DOCUMENT")
    print("-" * 60)
    print("Document ID:", document.document_id)
    print("Pages:", document.total_pages)
    print("Characters:", document.total_characters)

    print()
    print("CLAIMS")
    print("-" * 60)
    print("Claims extracted:", len(claims))

    print()
    print("SUMMARY")
    print("-" * 60)
    print(summary.summary)

    print()
    print("SELF-CROSS-QUESTIONING")
    print("-" * 60)
    print("Questions generated:", len(questions))
    print(
        "Verification results:",
        len(result["verification_results"]),
    )

    print()
    print("VERIFICATION SCORE")
    print("-" * 60)
    print("Factuality:", verification_score.factuality)
    print(
        "Evidence coverage:",
        verification_score.evidence_coverage,
    )
    print("Consistency:", verification_score.consistency)
    print("Completeness:", verification_score.completeness)
    print(
        "Numerical consistency:",
        verification_score.numerical_consistency,
    )
    print(
        "Contradiction penalty:",
        verification_score.contradiction_penalty,
    )
    print(
        "Overall score:",
        verification_score.overall_score,
    )

    print()
    print("DEVIL'S ADVOCATE")
    print("-" * 60)
    print("Challenges:", len(devil_report.results))
    print(
        "Overall score:",
        devil_report.overall_score,
    )

    print()
    print("REVISION")
    print("-" * 60)
    print("Version:", revision.version)
    print("Status:", revision.status)
    print("Score:", revision.verification_score)
    print("Reason:", revision.reason)

    print()
    print("=" * 60)
    print("PIPELINE TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()