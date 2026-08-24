from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.claims.extractor import ClaimExtractor
from backend.app.questioning.question_generator import (
    QuestionGenerator,
)


TEST_FILE = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("SELF-CROSS-QUESTIONING TEST")
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

    generator = QuestionGenerator()

    result = generator.generate(
        claims=claims,
    )

    print()
    print("QUESTIONS GENERATED")
    print("-" * 60)

    for question in result.questions:

        print(
            f"Question {question.question_id}"
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

        print()


if __name__ == "__main__":
    main()