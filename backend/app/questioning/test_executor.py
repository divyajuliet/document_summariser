from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.claims.extractor import ClaimExtractor
from backend.app.questioning.question_generator import QuestionGenerator
from backend.app.questioning.executor import QuestionExecutor


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("SELF-CROSS-QUESTIONING EXECUTION TEST")
    print("=" * 60)

    # --------------------------------------------------
    # EXTRACTION
    # --------------------------------------------------

    pipeline = ExtractionPipeline()

    document, attempts, validation = pipeline.extract(
        file_path=TEST_FILE,
        document_id="test-document",
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
    # QUESTION GENERATION
    # --------------------------------------------------

    generator = QuestionGenerator()

    # QuestionGenerator already has MAX_QUESTIONS = 10
    question_result = generator.generate(
        claims=claims,
    )

    questions = question_result.questions

    print(
        "Questions generated:",
        len(questions),
    )

    if not questions:
        print("No questions generated.")
        return

    # --------------------------------------------------
    # COLLECT ALL EVIDENCE
    # --------------------------------------------------

    all_evidence = [
        evidence
        for claim in claims
        for evidence in claim.evidence
    ]

    print(
        "Evidence items available:",
        len(all_evidence),
    )

    # --------------------------------------------------
    # QUESTION EXECUTOR
    # --------------------------------------------------

    executor = QuestionExecutor()

    print()
    print("VERIFICATION RESULTS")
    print("-" * 60)

    for index, question in enumerate(
        questions,
        start=1,
    ):

        # Find the claim associated with this question.
        claim = next(
            (
                item
                for item in claims
                if item.claim_id == question.claim_id
            ),
            None,
        )

        if claim is None:

            print(
                f"Question {index}: "
                f"Claim {question.claim_id} not found."
            )

            continue

        # --------------------------------------------------
        # EXECUTE QUESTION
        # --------------------------------------------------

        result = executor.execute(
            question=question,
            claim=claim,
            evidence=all_evidence,
            top_k=3,
        )

        # --------------------------------------------------
        # DISPLAY RESULT
        # --------------------------------------------------

        print(
            f"Question {index}"
        )

        print(
            f"Question ID: "
            f"{question.question_id}"
        )

        print(
            f"Claim ID: "
            f"{question.claim_id}"
        )

        print(
            f"Type: "
            f"{question.question_type}"
        )

        print(
            f"Priority: "
            f"{question.priority}"
        )

        print(
            f"Question: "
            f"{question.question}"
        )

        print(
            f"Status: "
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


if __name__ == "__main__":
    main()