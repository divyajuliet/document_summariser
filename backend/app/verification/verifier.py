import re
from typing import List

from backend.app.claims.models import (
    Claim,
    Evidence,
)

from backend.app.verification.models import (
    VerificationReport,
    VerificationResult,
)


class ClaimVerifier:

    def verify(
        self,
        claim: Claim,
        evidence: List[Evidence],
    ) -> VerificationReport:

        results = []

        if not evidence:

            results.append(
                VerificationResult(
                    claim_id=claim.claim_id,
                    claim_text=claim.claim_text,
                    verification_status="unsupported",
                    verification_score=0.0,
                    explanation=(
                        "No supporting evidence was "
                        "retrieved for this claim."
                    ),
                    evidence_pages=[],
                )
            )

            return VerificationReport(
                claim_id=claim.claim_id,
                results=results,
            )

        # --------------------------------------------------
        # FACTUAL / TEXTUAL VERIFICATION
        # --------------------------------------------------

        textual_result = self._verify_text(
            claim,
            evidence,
        )

        results.append(textual_result)

        # --------------------------------------------------
        # NUMERICAL VERIFICATION
        # --------------------------------------------------

        if claim.numbers:

            numerical_result = (
                self._verify_numbers(
                    claim,
                    evidence,
                )
            )

            results.append(
                numerical_result
            )

        # --------------------------------------------------
        # ENTITY VERIFICATION
        # --------------------------------------------------

        if claim.entities:

            entity_result = (
                self._verify_entities(
                    claim,
                    evidence,
                )
            )

            results.append(
                entity_result
            )

        # --------------------------------------------------
        # TEMPORAL VERIFICATION
        # --------------------------------------------------

        if claim.temporal_values:

            temporal_result = (
                self._verify_temporal(
                    claim,
                    evidence,
                )
            )

            results.append(
                temporal_result
            )

        return VerificationReport(
            claim_id=claim.claim_id,
            results=results,
        )

    # ======================================================
    # TEXT VERIFICATION
    # ======================================================

    @staticmethod
    def _verify_text(
        claim: Claim,
        evidence: List[Evidence],
    ) -> VerificationResult:

        claim_words = {
            word.lower().strip(
                ".,;:!?()[]{}\"'"
            )
            for word in claim.claim_text.split()
            if len(
                word.strip(
                    ".,;:!?()[]{}\"'"
                )
            ) >= 3
        }

        best_score = 0.0
        best_page = None

        for item in evidence:

            evidence_words = set(
                word.lower().strip(
                    ".,;:!?()[]{}\"'"
                )
                for word in item.text.split()
            )

            if not claim_words:
                continue

            matched = (
                claim_words
                & evidence_words
            )

            score = (
                len(matched)
                / len(claim_words)
            )

            if score > best_score:

                best_score = score
                best_page = item.page_number

        if best_score >= 0.8:

            status = "verified"

            explanation = (
                "The claim is strongly supported "
                "by the retrieved evidence."
            )

        elif best_score >= 0.5:

            status = "partially_supported"

            explanation = (
                "The retrieved evidence supports "
                "part of the claim."
            )

        else:

            status = "unsupported"

            explanation = (
                "The retrieved evidence does not "
                "strongly support the claim."
            )

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            verification_status=status,
            verification_score=round(
                best_score,
                3,
            ),
            explanation=explanation,
            evidence_pages=(
                [best_page]
                if best_page is not None
                else []
            ),
        )

    # ======================================================
    # NUMBER VERIFICATION
    # ======================================================

    @staticmethod
    def _verify_numbers(
        claim: Claim,
        evidence: List[Evidence],
    ) -> VerificationResult:

        claim_numbers = {
            number.text.lower()
            for number in claim.numbers
        }

        evidence_text = " ".join(
            item.text.lower()
            for item in evidence
        )

        matched = sum(
            1
            for number in claim_numbers
            if number in evidence_text
        )

        if not claim_numbers:

            score = 1.0

        else:

            score = (
                matched
                / len(claim_numbers)
            )

        if score == 1.0:

            status = "verified"

            explanation = (
                "All numerical values in the "
                "claim were found in the evidence."
            )

        elif score > 0:

            status = "partially_supported"

            explanation = (
                "Some numerical values in the "
                "claim were found in the evidence."
            )

        else:

            status = "unsupported"

            explanation = (
                "The numerical values in the "
                "claim were not found in the evidence."
            )

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            verification_status=status,
            verification_score=round(
                score,
                3,
            ),
            explanation=explanation,
            evidence_pages=[
                item.page_number
                for item in evidence
            ],
        )

    # ======================================================
    # ENTITY VERIFICATION
    # ======================================================

    @staticmethod
    def _verify_entities(
        claim: Claim,
        evidence: List[Evidence],
    ) -> VerificationResult:

        evidence_text = " ".join(
            item.text.lower()
            for item in evidence
        )

        entities = [
            entity.text.lower()
            for entity in claim.entities
        ]

        matched = sum(
            1
            for entity in entities
            if entity in evidence_text
        )

        if not entities:

            score = 1.0

        else:

            score = (
                matched
                / len(entities)
            )

        status = (
            "verified"
            if score == 1.0
            else (
                "partially_supported"
                if score > 0
                else "unsupported"
            )
        )

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            verification_status=status,
            verification_score=round(
                score,
                3,
            ),
            explanation=(
                f"{matched}/{len(entities)} "
                "entities were found in the "
                "retrieved evidence."
            ),
            evidence_pages=[
                item.page_number
                for item in evidence
            ],
        )

    # ======================================================
    # TEMPORAL VERIFICATION
    # ======================================================

    @staticmethod
    def _verify_temporal(
        claim: Claim,
        evidence: List[Evidence],
    ) -> VerificationResult:

        evidence_text = " ".join(
            item.text.lower()
            for item in evidence
        )

        temporal_values = [
            value.text.lower()
            for value in claim.temporal_values
        ]

        matched = sum(
            1
            for value in temporal_values
            if value in evidence_text
        )

        if not temporal_values:

            score = 1.0

        else:

            score = (
                matched
                / len(temporal_values)
            )

        status = (
            "verified"
            if score == 1.0
            else (
                "partially_supported"
                if score > 0
                else "unsupported"
            )
        )

        return VerificationResult(
            claim_id=claim.claim_id,
            claim_text=claim.claim_text,
            verification_status=status,
            verification_score=round(
                score,
                3,
            ),
            explanation=(
                f"{matched}/{len(temporal_values)} "
                "temporal values were found in "
                "the retrieved evidence."
            ),
            evidence_pages=[
                item.page_number
                for item in evidence
            ],
        )