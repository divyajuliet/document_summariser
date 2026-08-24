from backend.app.revision.manager import RevisionManager


def main():

    print("=" * 60)
    print("REVISION / ROLLBACK TEST")
    print("=" * 60)

    manager = RevisionManager()

    # --------------------------------------------------
    # Initial verified summary
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
    print("Summary:", initial.summary)

    # --------------------------------------------------
    # Better candidate
    # --------------------------------------------------

    improved = manager.evaluate_revision(
        summary="Improved verified summary.",
        verification_score=0.95,
    )

    print()
    print("IMPROVED REVISION")
    print("-" * 60)
    print("Version:", improved.version)
    print("Status:", improved.status)
    print("Score:", improved.verification_score)
    print("Summary:", improved.summary)
    print("Reason:", improved.reason)

    # --------------------------------------------------
    # Worse candidate
    # --------------------------------------------------

    worse = manager.evaluate_revision(
        summary="Bad candidate summary.",
        verification_score=0.60,
    )

    print()
    print("WORSE REVISION")
    print("-" * 60)
    print("Version:", worse.version)
    print("Status:", worse.status)
    print("Score:", worse.verification_score)
    print("Summary:", worse.summary)
    print("Reason:", worse.reason)

    # --------------------------------------------------
    # Final state
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