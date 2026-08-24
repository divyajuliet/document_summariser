from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)

from backend.app.extraction.quality import (
    ExtractionQualityEvaluator,
)


def main():

    document = ExtractedDocument(
        document_id="test-document",
        extraction_method="pdf_text",
        pages=[
            PageContent(
                page_number=1,
                text="This is a test document " * 30,
                char_count=len(
                    "This is a test document " * 30
                ),
            ),
            PageContent(
                page_number=2,
                text="Another page containing text " * 30,
                char_count=len(
                    "Another page containing text " * 30
                ),
            ),
        ],
    )

    evaluator = ExtractionQualityEvaluator()

    quality = evaluator.evaluate(
        document
    )

    print()
    print("=" * 60)
    print("EXTRACTION QUALITY")
    print("=" * 60)

    print(
        f"Score: {quality.score}"
    )

    print(
        f"Characters: {quality.total_characters}"
    )

    print(
        f"Pages with text: "
        f"{quality.pages_with_text}/"
        f"{quality.total_pages}"
    )

    print(
        f"Requires fallback: "
        f"{quality.requires_fallback}"
    )

    print(
        f"Reason: {quality.reason}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()