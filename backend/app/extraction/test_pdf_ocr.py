from pathlib import Path

from backend.app.extraction.ocr_extractor import (
    OCRExtractor,
)


PDF_PATH = Path(
    "uploads/63dc2d80-54e9-446d-9108-5e40f30ee653.pdf"
)


def main():

    if not PDF_PATH.exists():

        print(
            f"PDF not found: {PDF_PATH}"
        )

        return

    print("Starting PDF OCR...")

    extractor = OCRExtractor()

    pages = extractor.extract_pdf(
        PDF_PATH
    )

    print()
    print("=" * 60)
    print("PDF OCR RESULT")
    print("=" * 60)

    print(
        f"Pages processed: {len(pages)}"
    )

    total_characters = 0

    for index, text in enumerate(
        pages,
        start=1,
    ):

        print()
        print(
            f"--- PAGE {index} ---"
        )

        print(text[:1000])

        total_characters += len(text)

    print()
    print("=" * 60)

    print(
        f"Total characters: "
        f"{total_characters}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()