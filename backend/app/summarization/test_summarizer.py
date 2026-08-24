from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.summarization.summarizer import DocumentSummarizer


def main():

    print("=" * 60)
    print("SUMMARIZATION TEST")
    print("=" * 60)

    file_path = Path(
        "uploads"
    )

    pdf_files = list(
        file_path.glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF found in uploads folder."
        )

    pdf_path = pdf_files[0]

    print(f"\nTesting: {pdf_path.name}")

    pipeline = ExtractionPipeline()

    document, attempts, validation = (
        pipeline.extract(
            file_path=pdf_path,
            document_id="test-document",
        )
    )

    summarizer = DocumentSummarizer()

    result = summarizer.summarize(
        document
    )

    print("\n" + "=" * 60)
    print("SUMMARY RESULT")
    print("=" * 60)

    print(
        f"\nMethod: {result.method}"
    )

    print(
        f"Source characters: "
        f"{result.source_characters}"
    )

    print(
        f"Summary characters: "
        f"{result.summary_characters}"
    )

    print(
        f"Chunks processed: "
        f"{result.chunks_processed}"
    )

    print("\nSUMMARY")
    print("-" * 60)
    print(result.summary)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
