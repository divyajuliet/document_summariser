import re
from typing import List

from backend.app.claims.models import Claim
from backend.app.evidence.models import EvidenceItem
from backend.app.devils_advocate.models import (
    ChallengeResult,
    DevilAdvocateReport,
)


class DevilAdvocateChecker:

    MAX_CLAIMS = 10

    def check(
        self,
        claims: List[Claim],
        evidence: List[EvidenceItem],
    ) -> DevilAdvocateReport:

        prioritized_claims = sorted(
            claims,
            key=self._priority_score,
            reverse=True,
        )

        results = []

        for claim in prioritized_claims[
            : self.MAX_CLAIMS
        ]:

            related_evidence = self._related_evidence(
                claim,
                evidence,
            )

            challenge = self._build_challenge(
                claim
            )

            result = self._evaluate_challenge(
                claim=claim,
                challenge=challenge,
                evidence=related_evidence,
            )

            results.append(result)

        return DevilAdvocateReport(
            results=results
        )

    @staticmethod
    def _priority_score(
        claim: Claim,
    ) -> float:

        risk_scores = {
            "HIGH": 3.0,
            "MEDIUM": 2.0,
            "LOW": 1.0,
        }

        risk_score = risk_scores.get(
            claim.risk.upper(),
            1.0,
        )

        uncertainty = 1.0 - claim.confidence

        return risk_score + uncertainty

    @staticmethod
    def _related_evidence(
        claim: Claim,
        evidence: List[EvidenceItem],
    ) -> List[EvidenceItem]:

        claim_pages = {
            item.page_number
            for item in claim.evidence
        }

        related = [
            item
            for item in evidence
            if item.page_number in claim_pages
        ]

        return related

    @staticmethod
    def _build_challenge(
        claim: Claim,
    ) -> str:

        if claim.numbers:
            return (
                "Could the numerical values in this "
                "claim be incorrect or unsupported "
                "by the source evidence?"
            )

        if claim.temporal_values:
            return (
                "Could the date or time stated in this "
                "claim be incorrect or unsupported?"
            )

        if claim.entities:
            return (
                "Could the entities in this claim be "
                "incorrectly associated with the "
                "stated information?"
            )

        return (
            "Is there any source evidence that "
            "contradicts or weakens this claim?"
        )

    @classmethod
    def _evaluate_challenge(
        cls,
        claim: Claim,
        challenge: str,
        evidence: List[EvidenceItem],
    ) -> ChallengeResult:

        if not evidence:

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="issue",
                score=0.0,
                explanation=(
                    "No related source evidence was "
                    "available for the challenge."
                ),
                evidence_pages=[],
            )

        evidence_pages = sorted(
            {
                item.page_number
                for item in evidence
            }
        )

        # --------------------------------------------
        # NUMERICAL CHECK
        # --------------------------------------------

        if claim.numbers:

            claim_numbers = cls._extract_numbers(
                claim.claim_text
            )

            evidence_numbers = []

            for item in evidence:

                evidence_numbers.extend(
                    cls._extract_numbers(
                        item.evidence_text
                    )
                )

            missing_numbers = [
                number
                for number in claim_numbers
                if number not in evidence_numbers
            ]

            if not missing_numbers:

                return ChallengeResult(
                    claim_id=claim.claim_id,
                    challenge=challenge,
                    status="no_issue",
                    score=1.0,
                    explanation=(
                        "All numerical values in the "
                        "claim were found in the "
                        "related source evidence."
                    ),
                    evidence_pages=evidence_pages,
                )

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="review",
                score=0.5,
                explanation=(
                    "One or more numerical values in "
                    "the claim were not found in the "
                    "related source evidence."
                ),
                evidence_pages=evidence_pages,
            )

        # --------------------------------------------
        # ENTITY CHECK
        # --------------------------------------------

        if claim.entities:

            evidence_text = " ".join(
                item.evidence_text.lower()
                for item in evidence
            )

            missing_entities = []

            for entity in claim.entities:

                if (
                    entity.text.lower()
                    not in evidence_text
                ):
                    missing_entities.append(
                        entity.text
                    )

            if not missing_entities:

                return ChallengeResult(
                    claim_id=claim.claim_id,
                    challenge=challenge,
                    status="no_issue",
                    score=1.0,
                    explanation=(
                        "All identified entities in "
                        "the claim were found in the "
                        "related source evidence."
                    ),
                    evidence_pages=evidence_pages,
                )

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="review",
                score=0.5,
                explanation=(
                    "Some entities in the claim were "
                    "not found in the related evidence."
                ),
                evidence_pages=evidence_pages,
            )

        # --------------------------------------------
        # TEMPORAL CHECK
        # --------------------------------------------

        if claim.temporal_values:

            evidence_text = " ".join(
                item.evidence_text.lower()
                for item in evidence
            )

            missing_temporal = []

            for temporal in claim.temporal_values:

                if (
                    temporal.text.lower()
                    not in evidence_text
                ):
                    missing_temporal.append(
                        temporal.text
                    )

            if not missing_temporal:

                return ChallengeResult(
                    claim_id=claim.claim_id,
                    challenge=challenge,
                    status="no_issue",
                    score=1.0,
                    explanation=(
                        "The temporal values in the "
                        "claim were found in the "
                        "related source evidence."
                    ),
                    evidence_pages=evidence_pages,
                )

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="review",
                score=0.5,
                explanation=(
                    "Some temporal information in "
                    "the claim was not found in "
                    "the related evidence."
                ),
                evidence_pages=evidence_pages,
            )

        # --------------------------------------------
        # GENERAL FACTUAL CHECK
        # --------------------------------------------

        claim_words = cls._meaningful_words(
            claim.claim_text
        )

        evidence_text = " ".join(
            item.evidence_text.lower()
            for item in evidence
        )

        matching_words = sum(
            1
            for word in claim_words
            if word in evidence_text
        )

        if not claim_words:

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="review",
                score=0.5,
                explanation=(
                    "The claim did not contain enough "
                    "textual information for a "
                    "deterministic challenge."
                ),
                evidence_pages=evidence_pages,
            )

        support_ratio = (
            matching_words
            / len(claim_words)
        )

        if support_ratio >= 0.6:

            return ChallengeResult(
                claim_id=claim.claim_id,
                challenge=challenge,
                status="no_issue",
                score=1.0,
                explanation=(
                    "The majority of meaningful claim "
                    "terms are supported by the "
                    "related source evidence."
                ),
                evidence_pages=evidence_pages,
            )

        return ChallengeResult(
            claim_id=claim.claim_id,
            challenge=challenge,
            status="review",
            score=0.5,
            explanation=(
                "The retrieved evidence does not "
                "provide sufficient deterministic "
                "support for the claim."
            ),
            evidence_pages=evidence_pages,
        )

    @staticmethod
    def _extract_numbers(
        text: str,
    ) -> List[str]:

        return re.findall(
            r"\b\d+(?:\.\d+)?\b",
            text,
        )

    @staticmethod
    def _meaningful_words(
        text: str,
    ) -> List[str]:

        stop_words = {
            "the",
            "a",
            "an",
            "is",
            "are",
            "was",
            "were",
            "this",
            "that",
            "and",
            "or",
            "of",
            "to",
            "in",
            "on",
            "for",
            "with",
            "by",
            "from",
            "as",
        }

        words = re.findall(
            r"\b[a-zA-Z]{3,}\b",
            text.lower(),
        )

        return [
            word
            for word in words
            if word not in stop_words
        ]