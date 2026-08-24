from pathlib import Path

from backend.app.extraction.ocr_extractor import OCRExtractor


IMAGE_PATH = Path(
    "uploads/76bc68a6-e914-41d1-bab9-7c69d14ed7af.png"
)


def main():

    if not IMAGE_PATH.exists():
        print(f"Image not found: {IMAGE_PATH}")
        return

    print("Starting OCR...")

    extractor = OCRExtractor()

    text = extractor.extract_image(
        IMAGE_PATH
    )

    print()
    print("=" * 60)
    print("OCR RESULT")
    print("=" * 60)
    print()

    print(text)

    print()
    print("=" * 60)
    print(
        f"Characters extracted: {len(text)}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()