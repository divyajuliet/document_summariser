from pathlib import Path

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.summarization.chunker import DocumentChunker


def main():

    print("=" * 60)
    print("DOCUMENT CHUNKING TEST")
    print("=" * 60)

    upload_dir = Path("uploads")

    pdf_files = list(
        upload_dir.glob("*.pdf")
    )

    if not pdf_files:
        raise FileNotFoundError(
            "No PDF found in uploads folder."
        )

    pdf_path = pdf_files[0]

    print(
        f"\nTesting: {pdf_path.name}"
    )

    pipeline = ExtractionPipeline()

    document, attempts, validation = (
        pipeline.extract(
            file_path=pdf_path,
            document_id="test-document",
        )
    )

    chunker = DocumentChunker()

    chunks = chunker.chunk(
        document
    )

    print(
        f"\nPages: {document.total_pages}"
    )

    print(
        f"Characters: "
        f"{document.total_characters}"
    )

    print(
        f"Chunks created: "
        f"{len(chunks)}"
    )

    print("\nCHUNKS")
    print("-" * 60)

    for chunk in chunks:

        print(
            f"Chunk {chunk.chunk_id}: "
            f"Pages {chunk.page_start}-"
            f"{chunk.page_end} | "
            f"{chunk.character_count} characters"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
