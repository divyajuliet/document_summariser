from backend.app.revision.models import (
    SummaryRevision,
    RevisionHistory,
)


class RevisionManager:

    def __init__(self):
        self.history = RevisionHistory()

    def initialize(
        self,
        summary: str,
        verification_score: float,
    ) -> SummaryRevision:

        revision = SummaryRevision(
            version=1,
            summary=summary,
            verification_score=verification_score,
            status="accepted",
            reason="Initial verified summary.",
        )

        self.history.revisions.append(revision)
        self.history.best_version = 1

        return revision

    def evaluate_revision(
        self,
        summary: str,
        verification_score: float,
    ) -> SummaryRevision:

        if not self.history.revisions:
            return self.initialize(
                summary=summary,
                verification_score=verification_score,
            )

        previous_best = self._get_best_revision()

        new_version = len(
            self.history.revisions
        ) + 1

        if verification_score > previous_best.verification_score:

            revision = SummaryRevision(
                version=new_version,
                summary=summary,
                verification_score=verification_score,
                status="committed",
                reason=(
                    "Candidate revision improved "
                    "the verification score."
                ),
            )

            self.history.revisions.append(revision)
            self.history.best_version = new_version

        else:

            revision = SummaryRevision(
                version=new_version,
                summary=previous_best.summary,
                verification_score=previous_best.verification_score,
                status="rolled_back",
                reason=(
                    "Candidate revision did not improve "
                    "the verification score."
                ),
            )

            self.history.revisions.append(revision)

        return revision

    def _get_best_revision(
        self,
    ) -> SummaryRevision:

        return max(
            self.history.revisions,
            key=lambda revision: revision.verification_score,
        )

    @property
    def current_summary(self) -> str:

        return self._get_best_revision().summary

    @property
    def current_score(self) -> float:

        return self._get_best_revision().verification_score

    def get_history(self) -> RevisionHistory:

        return self.history