from pathlib import Path

from backend.app.extraction.pdf_extractor import PDFExtractor
from backend.app.summarization.llm_summarizer import LLMSummarizer


PDF_PATH = Path(
    "uploads/24d5655e-d67d-444e-9896-567cde443fc3.pdf"
)


def main():

    print("=" * 60)
    print("LLM SUMMARIZATION TEST")
    print("=" * 60)

    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        return

    print(f"\nTesting: {PDF_PATH.name}")

    # -----------------------------------------
    # EXTRACT DOCUMENT
    # -----------------------------------------

    extractor = PDFExtractor()

    document = extractor.extract(
        file_path=PDF_PATH,
        document_id="llm-test",
    )

    print("\nExtraction")
    print("-" * 60)
    print(f"Pages: {document.total_pages}")
    print(f"Characters: {document.total_characters}")

    # -----------------------------------------
    # INITIALIZE LLM
    # -----------------------------------------

    summarizer = LLMSummarizer()

    # -----------------------------------------
    # GENERATE SUMMARY
    # -----------------------------------------

    print("\nCalling LLM...")

    summary = summarizer.summarize(
        document=document,
        length="medium",
    )

    # -----------------------------------------
    # DISPLAY RESULT
    # -----------------------------------------

    print("\n" + "=" * 60)
    print("LLM SUMMARY")
    print("=" * 60)

    print(summary)

    print("\n" + "=" * 60)
    print("SUMMARY INFORMATION")
    print("=" * 60)

    print(f"Source characters: {document.total_characters}")
    print(f"Summary characters: {len(summary)}")


if __name__ == "__main__":
    main()