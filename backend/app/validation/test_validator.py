from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)

from backend.app.validation.validator import (
    ExtractionValidator,
)


def main():

    document = ExtractedDocument(
        document_id="validation-test",
        extraction_method="pdf_ocr",
        pages=[
            PageContent(
                page_number=1,
                text=(
                    "This is a sample extracted "
                    "document containing meaningful "
                    "text for validation testing."
                ),
                char_count=82,
            ),
            PageContent(
                page_number=2,
                text=(
                    "This is another page containing "
                    "additional extracted content."
                ),
                char_count=62,
            ),
        ],
    )

    validator = ExtractionValidator()

    result = validator.validate(
        document
    )

    print()
    print("=" * 60)
    print("SELF-CROSS-QUESTIONING TEST")
    print("=" * 60)

    print()
    print(
        f"Overall score: "
        f"{result.overall_score}"
    )

    print(
        f"Decision: "
        f"{result.decision}"
    )

    print()
    print("QUESTIONS")
    print("-" * 60)

    for index, question in enumerate(
        result.questions,
        start=1,
    ):

        print(
            f"{index}. "
            f"{question.question}"
        )

        print(
            f"   Passed: "
            f"{question.passed}"
        )

        print(
            f"   Score: "
            f"{question.score:.3f}"
        )

        print(
            f"   Explanation: "
            f"{question.explanation}"
        )

        print()

    print("=" * 60)


if __name__ == "__main__":
    main()