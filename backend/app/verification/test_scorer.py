from backend.app.verification.models import (
    VerificationResult,
)

from backend.app.verification.scorer import (
    VerificationScorer,
)


def main():

    print("=" * 60)
    print("VERIFICATION SCORER TEST")
    print("=" * 60)

    results = [
        VerificationResult(
            claim_id=1,
            claim_text="The system supports PDF upload.",
            verification_status="verified",
            verification_score=1.0,
            explanation=(
                "The claim is strongly supported "
                "by the retrieved source evidence."
            ),
            evidence_pages=[1],
        ),

        VerificationResult(
            claim_id=2,
            claim_text="The system supports OCR.",
            verification_status="verified",
            verification_score=1.0,
            explanation=(
                "The claim is strongly supported "
                "by the retrieved source evidence."
            ),
            evidence_pages=[2],
        ),

        VerificationResult(
            claim_id=3,
            claim_text="The system supports rollback.",
            verification_status="partially_verified",
            verification_score=0.5,
            explanation=(
                "The retrieved evidence provides "
                "partial support for the claim."
            ),
            evidence_pages=[5],
        ),
    ]

    scorer = VerificationScorer()

    score = scorer.score(
        results
    )

    print()
    print("VERIFICATION SCORE")
    print("-" * 60)

    print(
        "Factuality:",
        score.factuality,
    )

    print(
        "Evidence coverage:",
        score.evidence_coverage,
    )

    print(
        "Consistency:",
        score.consistency,
    )

    print(
        "Completeness:",
        score.completeness,
    )

    print(
        "Numerical consistency:",
        score.numerical_consistency,
    )

    print(
        "Contradiction penalty:",
        score.contradiction_penalty,
    )

    print()
    print(
        "Overall score:",
        score.overall_score,
    )


if __name__ == "__main__":
    main()