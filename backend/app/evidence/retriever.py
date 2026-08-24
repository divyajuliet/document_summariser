from typing import List

from backend.app.claims.models import (
    Claim,
    Evidence,
)

from backend.app.evidence.models import (
    EvidenceItem,
    EvidenceRetrievalResult,
)


class EvidenceRetriever:

    def retrieve(
        self,
        claim: Claim,
        evidence: List[Evidence],
        top_k: int = 5,
    ) -> EvidenceRetrievalResult:

        claim_text = claim.claim_text.strip()

        if not claim_text:

            return EvidenceRetrievalResult(
                claim_id=claim.claim_id,
                results=[],
            )

        # --------------------------------------------------
        # BUILD SEARCH TERMS
        # --------------------------------------------------

        query_terms = {
            word.lower().strip(
                ".,;:!?()[]{}\"'"
            )
            for word in claim_text.split()
            if len(
                word.strip(
                    ".,;:!?()[]{}\"'"
                )
            ) >= 3
        }

        if not query_terms:

            return EvidenceRetrievalResult(
                claim_id=claim.claim_id,
                results=[],
            )

        # --------------------------------------------------
        # SCORE EVIDENCE
        # --------------------------------------------------

        scored_evidence = []

        for item in evidence:

            evidence_text = item.text.strip()

            if not evidence_text:
                continue

            evidence_lower = (
                evidence_text.lower()
            )

            matched_terms = sum(
                1
                for term in query_terms
                if term in evidence_lower
            )

            if matched_terms == 0:
                continue

            relevance_score = (
                matched_terms
                / len(query_terms)
            )

            scored_evidence.append(
                (
                    relevance_score,
                    matched_terms,
                    item,
                )
            )

        # --------------------------------------------------
        # RANK EVIDENCE
        # --------------------------------------------------

        scored_evidence.sort(
            key=lambda item: (
                item[0],
                item[1],
            ),
            reverse=True,
        )

        # --------------------------------------------------
        # BUILD RESULTS
        # --------------------------------------------------

        results = []

        for (
            relevance_score,
            _matched_terms,
            item,
        ) in scored_evidence[:top_k]:

            results.append(
                EvidenceItem(
                    page_number=item.page_number,
                    evidence_text=item.text,
                    relevance_score=round(
                        relevance_score,
                        3,
                    ),
                )
            )

        return EvidenceRetrievalResult(
            claim_id=claim.claim_id,
            results=results,
        )