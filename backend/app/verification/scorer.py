from typing import List

from backend.app.verification.models import (
    VerificationResult,
)
from backend.app.revision.models import VerificationScore


class VerificationScorer:

    def score(
        self,
        results: List[VerificationResult],
    ) -> VerificationScore:

        if not results:
            return VerificationScore()

        total = len(results)

        verified = sum(
            1
            for result in results
            if result.verification_status
            == "verified"
        )

        partially_verified = sum(
            1
            for result in results
            if result.verification_status
            == "partially_verified"
        )

        unverified = sum(
            1
            for result in results
            if result.verification_status
            == "unverified"
        )

        # ----------------------------------------------
        # FACTUALITY
        # ----------------------------------------------

        factuality = (
            verified
            + (0.5 * partially_verified)
        ) / total

        # ----------------------------------------------
        # EVIDENCE COVERAGE
        # ----------------------------------------------

        with_evidence = sum(
            1
            for result in results
            if result.evidence_pages
        )

        evidence_coverage = (
            with_evidence / total
        )

        # ----------------------------------------------
        # CONSISTENCY
        # ----------------------------------------------

        consistency = (
            sum(
                result.verification_score
                for result in results
            )
            / total
        )

        # ----------------------------------------------
        # NUMERICAL CONSISTENCY
        # ----------------------------------------------

        numerical_results = [
            result
            for result in results
            if "numerical" in result.explanation.lower()
            or "numerical" in result.claim_text.lower()
        ]

        if numerical_results:

            numerical_consistency = (
                sum(
                    result.verification_score
                    for result in numerical_results
                )
                / len(numerical_results)
            )

        else:

            numerical_consistency = consistency

        # ----------------------------------------------
        # COMPLETENESS
        # ----------------------------------------------

        completeness = evidence_coverage

        # ----------------------------------------------
        # CONTRADICTION PENALTY
        # ----------------------------------------------

        contradictions = sum(
            1
            for result in results
            if result.verification_status
            == "contradicted"
        )

        contradiction_penalty = (
            contradictions / total
        )

        return VerificationScore(
            factuality=round(
                factuality,
                3,
            ),
            evidence_coverage=round(
                evidence_coverage,
                3,
            ),
            consistency=round(
                consistency,
                3,
            ),
            completeness=round(
                completeness,
                3,
            ),
            numerical_consistency=round(
                numerical_consistency,
                3,
            ),
            contradiction_penalty=round(
                contradiction_penalty,
                3,
            ),
        )