import os
from typing import List

from google import genai

from backend.app.extraction.models import ExtractedDocument
from backend.app.summarization.models import SummaryResult
from backend.app.summarization.chunker import (
    DocumentChunk,
    DocumentChunker,
)


class DocumentSummarizer:

    def __init__(self):

        # --------------------------------------------------
        # GEMINI API CONFIGURATION
        # --------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        # Gemma model
        self.model = "gemma-4-26b-a4b-it"

        # Document chunking
        self.chunker = DocumentChunker()

    # ======================================================
    # MAIN SUMMARIZATION
    # ======================================================

    def summarize(
        self,
        document: ExtractedDocument,
    ) -> SummaryResult:

        # --------------------------------------------------
        # CREATE DOCUMENT CHUNKS
        # --------------------------------------------------

        chunks = self.chunker.chunk(document)

        if not chunks:
            raise ValueError(
                "Cannot summarize an empty document."
            )

        # --------------------------------------------------
        # SUMMARIZE EACH CHUNK
        # --------------------------------------------------

        chunk_summaries: List[str] = []

        for chunk in chunks:

            summary = self._summarize_chunk(
                chunk
            )

            if summary:
                chunk_summaries.append(
                    summary.strip()
                )

        if not chunk_summaries:
            raise RuntimeError(
                "The LLM did not produce any summaries."
            )

        # --------------------------------------------------
        # COMBINE CHUNK SUMMARIES
        # --------------------------------------------------

        final_summary = self._combine_summaries(
            chunk_summaries
        )

        # --------------------------------------------------
        # RETURN RESULT
        # --------------------------------------------------

        return SummaryResult(
            document_id=document.document_id,
            summary=final_summary,
            source_characters=document.total_characters,
            summary_characters=len(final_summary),
            chunks_processed=len(chunks),
            method="gemma_chunked",
        )

    # ======================================================
    # SUMMARIZE SINGLE CHUNK
    # ======================================================

    def _summarize_chunk(
        self,
        chunk: DocumentChunk,
    ) -> str:

        prompt = f"""
You are a document summarization system.

Summarize the following document section accurately.

Rules:
- Use ONLY information present in the provided text.
- Do not invent facts.
- Preserve important names, numbers, dates, requirements,
  decisions, and technical terms.
- Remove repetition and unnecessary wording.
- Keep the summary concise but informative.
- Do not mention that you are an AI.
- Do not add information from outside the document.

The text comes from pages {chunk.page_start}
through {chunk.page_end}.

DOCUMENT SECTION:
--------------------------------------------------
{chunk.text}
--------------------------------------------------

SUMMARY:
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )

        # --------------------------------------------------
        # SAFELY EXTRACT RESPONSE TEXT
        # --------------------------------------------------

        if not response:
            return ""

        text = getattr(
            response,
            "text",
            None,
        )

        if not text:
            return ""

        return text.strip()

    # ======================================================
    # COMBINE CHUNK SUMMARIES
    # ======================================================

    @staticmethod
    def _combine_summaries(
        summaries: List[str],
    ) -> str:

        cleaned_summaries = [
            summary.strip()
            for summary in summaries
            if summary
            and summary.strip()
        ]

        return "\n\n".join(
            cleaned_summaries
        )