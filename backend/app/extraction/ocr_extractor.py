from pathlib import Path

import pytesseract
import pymupdf

from PIL import Image


TESSERACT_PATH = Path(
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


class OCRExtractor:

    def __init__(self):
        self._configure_tesseract()

    @staticmethod
    def _configure_tesseract():
        """
        Configure the Tesseract executable explicitly.
        This avoids depending on the Windows PATH.
        """

        if not TESSERACT_PATH.exists():
            raise FileNotFoundError(
                f"Tesseract executable not found at: "
                f"{TESSERACT_PATH}"
            )

        pytesseract.pytesseract.tesseract_cmd = str(
            TESSERACT_PATH
        )

    # --------------------------------------------------
    # IMAGE OCR
    # --------------------------------------------------

    def extract_image(
        self,
        file_path: Path,
    ) -> str:

        image = Image.open(file_path)

        try:
            text = pytesseract.image_to_string(
                image
            )
        finally:
            image.close()

        return self._normalize_text(text)

    # --------------------------------------------------
    # PDF OCR
    # --------------------------------------------------

    def extract_pdf(
        self,
        file_path: Path,
    ) -> list[str]:

        document = pymupdf.open(file_path)
        page_texts = []
        try:
            if document.needs_pass:
                raise ValueError(
                    "PDF is password-protected. "
                    "A password is required for OCR extraction."
                    )

            for page in document:

                # Render PDF page as an image.
                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                    )

                image = Image.frombytes(
                    "RGB",
                    [
                        pixmap.width,
                        pixmap.height,
                    ],
                    pixmap.samples,
                )

                try:

                    text = pytesseract.image_to_string(
                        image
                    )

                    page_texts.append(
                        self._normalize_text(text)
                    )

                finally:
                    image.close()

        finally:
            document.close()

        return page_texts

    # --------------------------------------------------
    # TEXT NORMALIZATION
    # --------------------------------------------------

    @staticmethod
    def _normalize_text(
        text: str,
    ) -> str:

        lines = [
            line.strip()
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)