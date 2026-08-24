import os

from google import genai

from backend.app.extraction.models import ExtractedDocument


class LLMSummarizer:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-3.6-flash"

    def summarize(
        self,
        document: ExtractedDocument,
        length: str = "medium",
    ) -> str:

        full_text = "\n\n".join(
            f"[Page {page.page_number}]\n{page.text}"
            for page in document.pages
            if page.text.strip()
        )

        if not full_text.strip():
            raise ValueError(
                "Cannot summarize an empty document."
            )

        length_instructions = {
            "short": (
                "Give a concise summary in about "
                "5-8 sentences."
            ),
            "medium": (
                "Give a clear summary covering the "
                "important points and major sections."
            ),
            "long": (
                "Give a detailed summary covering "
                "all major sections and important details."
            ),
        }

        instruction = length_instructions.get(
            length,
            length_instructions["medium"],
        )

        prompt = f"""
You are a document summarization assistant.

Summarize ONLY information supported by the
provided document.

Do not invent facts.
Do not add outside information.

Preserve important:
- names
- numbers
- dates
- technical details
- requirements
- conclusions

{instruction}

DOCUMENT:

{full_text}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text