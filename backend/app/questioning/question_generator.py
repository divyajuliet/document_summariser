from typing import List

from backend.app.claims.models import Claim
from backend.app.questioning.models import (
    VerificationQuestion,
    QuestionGenerationResult,
)


class QuestionGenerator:

    MAX_QUESTIONS = 10

    def generate(
        self,
        claims: List[Claim],
    ) -> QuestionGenerationResult:

        questions = []

        # Prioritize claims based on risk and confidence.
        prioritized_claims = sorted(
            claims,
            key=self._priority_score,
            reverse=True,
        )

        question_id = 1

        for claim in prioritized_claims:

            question_type = self._determine_question_type(
                claim
            )

            if question_type is None:
                continue

            question = self._build_question(
                claim,
                question_type,
            )

            priority = self._determine_priority(
                claim
            )

            questions.append(
                VerificationQuestion(
                    question_id=question_id,
                    claim_id=claim.claim_id,
                    question=question,
                    question_type=question_type,
                    priority=priority,
                )
            )

            question_id += 1

            if len(questions) >= self.MAX_QUESTIONS:
                break

        return QuestionGenerationResult(
            questions=questions
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

        # Lower confidence means higher verification priority.
        uncertainty = 1.0 - claim.confidence

        return risk_score + uncertainty

    @staticmethod
    def _determine_priority(
        claim: Claim,
    ) -> str:

        risk = claim.risk.upper()

        if risk == "HIGH" or claim.confidence < 0.5:
            return "HIGH"

        if risk == "MEDIUM" or claim.confidence < 0.75:
            return "MEDIUM"

        return "LOW"

    @staticmethod
    def _determine_question_type(
        claim: Claim,
    ) -> str | None:

        claim_type = claim.claim_type.lower()

        if claim.numbers:
            return "numerical"

        if claim.temporal_values:
            return "temporal"

        if claim.entities:
            return "entity"

        if "caus" in claim_type:
            return "causality"

        if "contradict" in claim_type:
            return "contradiction"

        if "complete" in claim_type:
            return "completeness"

        return "factual"

    @staticmethod
    def _build_question(
        claim: Claim,
        question_type: str,
    ) -> str:

        questions = {
            "factual": (
                "Is this claim directly supported "
                "by the source evidence?"
            ),

            "numerical": (
                "Does the source evidence explicitly "
                "support the numerical values stated "
                "in this claim?"
            ),

            "entity": (
                "Does the source evidence correctly "
                "associate the identified entities "
                "with this claim?"
            ),

            "temporal": (
                "Does the source evidence support the "
                "date or time stated in this claim?"
            ),

            "causality": (
                "Does the source evidence establish "
                "the stated cause-and-effect relationship?"
            ),

            "contradiction": (
                "Does any source evidence contradict "
                "this claim?"
            ),

            "completeness": (
                "Does this claim contain all important "
                "information supported by the source?"
            ),
        }

        return questions.get(
            question_type,
            questions["factual"],
        )