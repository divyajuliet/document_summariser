from typing import List

from backend.app.extraction.pipeline import ExtractionPipeline
from backend.app.claims.extractor import ClaimExtractor
from backend.app.evidence.retriever import EvidenceRetriever
from backend.app.questioning.question_generator import QuestionGenerator
from backend.app.questioning.executor import QuestionExecutor
from backend.app.verification.scorer import VerificationScorer
from backend.app.devils_advocate.checker import DevilAdvocateChecker
from backend.app.revision.manager import RevisionManager
from backend.app.summarization.summarizer import DocumentSummarizer


class DocumentIntelligencePipeline:

    def __init__(self):

        self.extraction = ExtractionPipeline()
        self.claim_extractor = ClaimExtractor()
        self.evidence_retriever = EvidenceRetriever()
        self.question_generator = QuestionGenerator()
        self.question_executor = QuestionExecutor()
        self.verification_scorer = VerificationScorer()
        self.devils_advocate = DevilAdvocateChecker()
        self.summarizer = DocumentSummarizer()
        self.revision_manager = RevisionManager()

    def process(
        self,
        file_path,
        document_id: str,
    ):

        # --------------------------------------------------
        # 1. EXTRACTION
        # --------------------------------------------------

        document, attempts, validation = (
            self.extraction.extract(
                file_path=file_path,
                document_id=document_id,
            )
        )

        # --------------------------------------------------
        # 2. CLAIM EXTRACTION
        # --------------------------------------------------

        claims = self.claim_extractor.extract(
            document=document
        )

        # --------------------------------------------------
        # 3. COLLECT EVIDENCE
        # --------------------------------------------------

        all_evidence = [
            evidence
            for claim in claims
            for evidence in claim.evidence
        ]

        # --------------------------------------------------
        # 4. INITIAL SUMMARY
        # --------------------------------------------------

        summary_result = self.summarizer.summarize(
            document
        )

        # --------------------------------------------------
        # 5. SELF-CROSS-QUESTIONING
        # --------------------------------------------------

        question_result = (
            self.question_generator.generate(
                claims=claims
            )
        )

        questions = question_result.questions

        verification_results = []

        for question in questions:

            claim = next(
                (
                    claim
                    for claim in claims
                    if claim.claim_id == question.claim_id
                ),
                None,
            )

            if claim is None:
                continue

            evidence_result = (
                self.evidence_retriever.retrieve(
                    claim=claim,
                    evidence=all_evidence,
                )
            )

            result = self.question_executor.execute(
                question=question,
                claim=claim,
                evidence=evidence_result.results,
            )

            verification_results.append(result)

        # --------------------------------------------------
        # 6. VERIFICATION SCORE
        # --------------------------------------------------

        verification_score = (
            self.verification_scorer.score(
                verification_results
            )
        )

        # --------------------------------------------------
        # 7. DEVIL'S ADVOCATE
        # --------------------------------------------------

        devil_report = (
            self.devils_advocate.check(
                claims=claims,
                evidence=all_evidence,
            )
        )

        # --------------------------------------------------
        # 8. INITIALIZE REVISION HISTORY
        # --------------------------------------------------

        initial_revision = (
            self.revision_manager.initialize(
                summary=summary_result.summary,
                verification_score=(
                    verification_score.overall_score
                ),
            )
        )

        # --------------------------------------------------
        # 9. RETURN COMPLETE RESULT
        # --------------------------------------------------

        return {
            "document": document,
            "claims": claims,
            "summary": summary_result,
            "questions": questions,
            "verification_results": verification_results,
            "verification_score": verification_score,
            "devils_advocate": devil_report,
            "revision": initial_revision,
            "attempts": attempts,
            "validation": validation,
        }