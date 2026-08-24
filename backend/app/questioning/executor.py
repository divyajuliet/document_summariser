from dataclasses import dataclass
from typing import List

from backend.app.claims.models import Claim, Evidence
from backend.app.evidence.retriever import EvidenceRetriever
from backend.app.questioning.models import VerificationQuestion
from backend.app.verification.models import VerificationResult


@dataclass
class QuestionAnswer:
    question_id: int
    claim_id: int
    question: str
    answer: str
    evidence_pages: List[int]
    confidence: float
    verification_status: str
    explanation: str


class QuestionExecutor:

    def __init__(self):
        self.retriever = EvidenceRetriever()

    def execute(
        self,
        question: VerificationQuestion,
        claim: Claim,
        evidence: List[Evidence],
        top_k: int = 3,
    ) -> VerificationResult:

        # --------------------------------------------------
        # RETRIEVE RELEVANT EVIDENCE
        # --------------------------------------------------

        retrieval_result = self.retriever.retrieve(
            claim=claim,
            evidence=evidence,
            top_k=top_k,
        )

        retrieved = retrieval_result.results

        # --------------------------------------------------
        # NO EVIDENCE
        # --------------------------------------------------

        if not retrieved:

            return VerificationResult(
                claim_id=claim.claim_id,
                claim_text=claim.claim_text,
                verification_status="unverified",
                verification_score=0.0,
                explanation=(
                    "No supporting evidence was retrieved "
                    "for this verification question."
                ),
                evidence_pages=[],
            )

        # --------------------------------------------------
        # EVIDENCE PAGES
        # --------------------------------------------------

        evidence_pages = list(
            dict.fromkeys(
                item.page_number
                for item in retrieved
            )
        )

        # --------------------------------------------------
        # BEST EVIDENCE
        # --------------------------------------------------

        best_evidence = retrieved[0]

        best_score = float(
            best_evidence.relevance_score
        )

        # --------------------------------------------------
        # DETERMINE VERIFICATION STATUS
        # --------------------------------------------------

        if best_score >= 0.75:

            status = "verified"

            explanation = (
                "The claim is strongly supported "
                "by the retrieved source evidence."
            )

        elif best_score >= 0.40:

            status = "partially_verified"

            explanation = (
                "The retrieved evidence provides "
                "partial support for the claim."
            )

        else:

            status = "unverified"

            explanation = (
                "The retrieved evidence does not "
                "provide strong enough support for "
                "the claim."
            )

        # --------------------------------------------------
        # CREATE VERIFICATION RESULT
        # --------------------------------------------------

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            verification_status=status,
            verification_score=round(
                best_score,
                3,
            ),
            explanation=explanation,
            evidence_pages=evidence_pages,
        )