from backend.app.revision.models import (
    SummaryRevision,
    RevisionHistory,
)
from backend.app.devils_advocate.models import (
    DevilAdvocateReport,
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
        devil_advocate_report: DevilAdvocateReport | None = None,
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

        # --------------------------------------------------
        # CHECK 1: VERIFICATION SCORE
        # --------------------------------------------------

        score_improved = (
            verification_score
            > previous_best.verification_score
        )

        # --------------------------------------------------
        # CHECK 2: DEVIL'S ADVOCATE
        # --------------------------------------------------

        serious_issue = False

        if devil_advocate_report is not None:

            serious_issue = any(
                result.status in {
                    "contradiction",
                    "high_risk",
                }
                for result in devil_advocate_report.results
            )

        # --------------------------------------------------
        # COMMIT
        # --------------------------------------------------

        if score_improved and not serious_issue:

            revision = SummaryRevision(
                version=new_version,
                summary=summary,
                verification_score=verification_score,
                status="committed",
                reason=(
                    "Candidate revision improved "
                    "the verification score and "
                    "no serious Devil's Advocate "
                    "issues were detected."
                ),
            )

            self.history.revisions.append(revision)
            self.history.best_version = new_version

            return revision

        # --------------------------------------------------
        # ROLLBACK
        # --------------------------------------------------

        if serious_issue:

            reason = (
                "Candidate revision was rolled back "
                "because the Devil's Advocate detected "
                "a serious contradiction or high-risk issue."
            )

        else:

            reason = (
                "Candidate revision did not improve "
                "the verification score."
            )

        revision = SummaryRevision(
            version=new_version,
            summary=previous_best.summary,
            verification_score=previous_best.verification_score,
            status="rolled_back",
            reason=reason,
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