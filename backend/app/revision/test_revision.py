from backend.app.revision.manager import RevisionManager
from backend.app.devils_advocate.models import (
    ChallengeResult,
    DevilAdvocateReport,
)


def main():

    print("=" * 60)
    print("CONDITIONAL REVISION / ROLLBACK TEST")
    print("=" * 60)

    manager = RevisionManager()

    # --------------------------------------------------
    # INITIAL SUMMARY
    # --------------------------------------------------

    initial = manager.initialize(
        summary="Initial verified summary.",
        verification_score=0.90,
    )

    print()
    print("INITIAL REVISION")
    print("-" * 60)
    print("Version:", initial.version)
    print("Status:", initial.status)
    print("Score:", initial.verification_score)

    # --------------------------------------------------
    # CASE 1: SCORE IMPROVES + NO ISSUE
    # --------------------------------------------------

    clean_report = DevilAdvocateReport(
        results=[
            ChallengeResult(
                claim_id=1,
                challenge="Could this claim be incorrect?",
                status="no_issue",
                score=1.0,
                explanation="Evidence supports the claim.",
                evidence_pages=[1],
            )
        ]
    )

    committed = manager.evaluate_revision(
        summary="Improved verified summary.",
        verification_score=0.95,
        devil_advocate_report=clean_report,
    )

    print()
    print("CASE 1: IMPROVED + NO SERIOUS ISSUE")
    print("-" * 60)
    print("Version:", committed.version)
    print("Status:", committed.status)
    print("Score:", committed.verification_score)
    print("Summary:", committed.summary)
    print("Reason:", committed.reason)

    # --------------------------------------------------
    # CASE 2: SCORE IMPROVES BUT CONTRADICTION EXISTS
    # --------------------------------------------------

    contradiction_report = DevilAdvocateReport(
        results=[
            ChallengeResult(
                claim_id=2,
                challenge="Could this claim be incorrect?",
                status="contradiction",
                score=0.0,
                explanation="Source evidence contradicts the claim.",
                evidence_pages=[4],
            )
        ]
    )

    rolled_back = manager.evaluate_revision(
        summary="Contradictory candidate summary.",
        verification_score=0.98,
        devil_advocate_report=contradiction_report,
    )

    print()
    print("CASE 2: IMPROVED BUT CONTRADICTION")
    print("-" * 60)
    print("Version:", rolled_back.version)
    print("Status:", rolled_back.status)
    print("Score:", rolled_back.verification_score)
    print("Summary:", rolled_back.summary)
    print("Reason:", rolled_back.reason)

    # --------------------------------------------------
    # CASE 3: SCORE GETS WORSE
    # --------------------------------------------------

    worse = manager.evaluate_revision(
        summary="Worse candidate summary.",
        verification_score=0.60,
        devil_advocate_report=clean_report,
    )

    print()
    print("CASE 3: SCORE GETS WORSE")
    print("-" * 60)
    print("Version:", worse.version)
    print("Status:", worse.status)
    print("Score:", worse.verification_score)
    print("Summary:", worse.summary)
    print("Reason:", worse.reason)

    # --------------------------------------------------
    # FINAL STATE
    # --------------------------------------------------

    print()
    print("FINAL STATE")
    print("-" * 60)
    print("Best version:", manager.history.best_version)
    print("Best score:", manager.current_score)
    print("Current summary:", manager.current_summary)

    print()
    print("REVISION HISTORY")
    print("-" * 60)

    for revision in manager.history.revisions:

        print(
            f"Version {revision.version} | "
            f"{revision.status} | "
            f"Score: {revision.verification_score}"
        )


if __name__ == "__main__":
    main()