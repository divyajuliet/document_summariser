from backend.app.extraction.models import (
    ExtractedDocument,
    PageContent,
)

from backend.app.extraction.quality import (
    ExtractionQualityEvaluator,
)


def main():

    # --------------------------------------------------
    # TEST DOCUMENT
    # --------------------------------------------------

    document = ExtractedDocument(
        document_id="quality-test",

        extraction_method="pdf_text",

        pages=[
            PageContent(
                page_number=1,
                text=(
                    "This is a sample document containing "
                    "meaningful extracted text. "
                    "The purpose of this test is to evaluate "
                    "the quality of the extraction pipeline."
                ),
                char_count=(
                    len(
                        "This is a sample document containing "
                        "meaningful extracted text. "
                        "The purpose of this test is to evaluate "
                        "the quality of the extraction pipeline."
                    )
                ),
            ),

            PageContent(
                page_number=2,
                text=(
                    "The second page also contains meaningful "
                    "content. This allows us to test page "
                    "coverage and structural consistency."
                ),
                char_count=(
                    len(
                        "The second page also contains meaningful "
                        "content. This allows us to test page "
                        "coverage and structural consistency."
                    )
                ),
            ),
        ],
    )

    # --------------------------------------------------
    # EVALUATE
    # --------------------------------------------------

    evaluator = ExtractionQualityEvaluator()

    result = evaluator.evaluate(
        document
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print()
    print("=" * 60)
    print("QEXT QUALITY SCORING TEST")
    print("=" * 60)

    print()

    print(
        f"Overall Score: "
        f"{result.score}"
    )

    print(
        f"Requires Fallback: "
        f"{result.requires_fallback}"
    )

    print(
        f"Reason: "
        f"{result.reason}"
    )

    print()

    print("QUALITY DIMENSIONS")
    print("-" * 60)

    print(
        f"Text Completeness: "
        f"{result.text_completeness}"
    )

    print(
        f"Page Coverage: "
        f"{result.page_coverage}"
    )

    print(
        f"Character Quality: "
        f"{result.character_quality}"
    )

    print(
        f"Structural Consistency: "
        f"{result.structural_consistency}"
    )

    print(
        f"Suspicious Character Score: "
        f"{result.suspicious_character_score}"
    )

    print(
        f"Text Density: "
        f"{result.text_density}"
    )

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()