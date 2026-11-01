
from uuid import UUID

from sqlalchemy import or_, select

from app.db.database import SessionLocal
from app.enums.processing_job_status import ProcessingJobStatus
from app.models.document_model import Document
from app.models.processing_job_model import ProcessingJob


ACTIVE_JOB_STATUSES = (
    ProcessingJobStatus.PENDING,
    ProcessingJobStatus.RUNNING,
)


def get_progress_rows(
    tracked_job_ids: set[UUID],
) -> list[dict]:
    """Fetch active jobs and tracked jobs that may have finished."""

    with SessionLocal() as db:
        active_condition = ProcessingJob.status.in_(
            ACTIVE_JOB_STATUSES
        )

        if tracked_job_ids:
            job_condition = or_(
                active_condition,
                ProcessingJob.id.in_(tracked_job_ids),
            )
        else:
            job_condition = active_condition

        statement = (
            select(
                Document.id.label("document_id"),
                Document.status.label("document_status"),
                ProcessingJob.id.label("job_id"),
                ProcessingJob.status.label("job_status"),
                ProcessingJob.locked_until.label("locked_until"),
                ProcessingJob.next_attempt_at.label("next_attempt_at"),
                ProcessingJob.created_at.label("created_at"),
            )
            .join(
                ProcessingJob,
                ProcessingJob.document_id == Document.id,
            )
            .where(job_condition)
            .order_by(ProcessingJob.created_at)
        )

        rows = db.execute(statement).mappings().all()
        return [dict(row) for row in rows]
