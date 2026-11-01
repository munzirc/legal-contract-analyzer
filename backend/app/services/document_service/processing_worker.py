import uuid
import logging
import threading
import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import case, or_, select, update
from app.enums.document_status import DocumentStatus
from app.models.document_model import Document

from app.db.database import SessionLocal
from app.enums.processing_job_status import ProcessingJobStatus
from app.models.processing_job_model import ProcessingJob
from app.services.document_service.process_document import process_document

logger = logging.getLogger(__name__)

LEASE_RENEW_INTERVAL = timedelta(seconds=30)
WORKER_IDLE_INTERVAL = 5

LEASE_DURATION = timedelta(minutes=2)
MAX_ATTEMPTS = 3

RETRY_DELAYS_SECONDS = {
    1: 10,
    2: 30,
}


def claim_next_job() -> tuple[uuid.UUID, uuid.UUID] | None:
    now = datetime.now(timezone.utc)
    lease_token = uuid.uuid4()

    with SessionLocal() as db:
        with db.begin():
            # Expired jobs that have exhausted their attempts
            # must become FAILED instead of remaining RUNNING forever.
            db.execute(
                update(ProcessingJob)
                .where(
                    ProcessingJob.status == ProcessingJobStatus.RUNNING,
                    ProcessingJob.attempt_count >= MAX_ATTEMPTS,
                    or_(
                        ProcessingJob.locked_until < now,
                        ProcessingJob.locked_until.is_(None),
                    ),
                )
                .values(
                    status=ProcessingJobStatus.FAILED,
                    finished_at=now,
                    locked_until=None,
                    lease_token=None,
                    last_error="Maximum attempts reached; processing lease expired.",
                )
            )

            # Claim a pending job or recover an expired job,
            # provided it has attempts remaining.
            statement = (
                select(ProcessingJob)
                .where(
                    ProcessingJob.attempt_count < MAX_ATTEMPTS,
                    or_(
                        ProcessingJob.next_attempt_at.is_(None),
                        ProcessingJob.next_attempt_at <= now,
                    ),
                    or_(
                        ProcessingJob.status == ProcessingJobStatus.PENDING,
                        (
                            (ProcessingJob.status == ProcessingJobStatus.RUNNING)
                            & or_(
                                ProcessingJob.locked_until < now,
                                ProcessingJob.locked_until.is_(None),
                            )
                        ),
                    ),
                )
                .order_by(
                    case(
                        (
                            ProcessingJob.status == ProcessingJobStatus.PENDING,
                            0,
                        ),
                        else_=1,
                    ),
                    ProcessingJob.created_at,
                )
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            job = db.scalars(statement).first()

            if job is None:
                return None
         
            job.status = ProcessingJobStatus.RUNNING
            job.next_attempt_at = None
            job.attempt_count += 1
            job.started_at = now
            job.finished_at = None
            job.locked_until = now + LEASE_DURATION
            job.lease_token = lease_token
            job.last_error = None

            return job.id, lease_token

        
def renew_lease(
    job_id: uuid.UUID,
    lease_token: uuid.UUID,
) -> bool:
    now = datetime.now(timezone.utc)
    new_locked_until = now + LEASE_DURATION

    with SessionLocal() as db:
        with db.begin():
            statement = (
                select(ProcessingJob)
                .where(
                    ProcessingJob.id == job_id,
                    ProcessingJob.status == ProcessingJobStatus.RUNNING,
                    ProcessingJob.lease_token == lease_token,
                    ProcessingJob.locked_until > now,
                )
                .with_for_update()
            )

            job = db.scalars(statement).first()

            if job is None:
                return False

            job.locked_until = new_locked_until

    return True

def complete_job(
    job_id: uuid.UUID,
    lease_token: uuid.UUID,
) -> bool:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        with db.begin():
            statement = (
                select(ProcessingJob)
                .where(
                    ProcessingJob.id == job_id,
                    ProcessingJob.status == ProcessingJobStatus.RUNNING,
                    ProcessingJob.lease_token == lease_token,
                    ProcessingJob.locked_until > now,
                )
                .with_for_update()
            )

            job = db.scalars(statement).first()

            if job is None:
                return False

            job.status = ProcessingJobStatus.COMPLETED
            job.finished_at = now
            job.locked_until = None
            job.lease_token = None
            job.last_error = None

    return True

def fail_job(
    job_id: uuid.UUID,
    lease_token: uuid.UUID,
    error: Exception,
) -> bool:
    now = datetime.now(timezone.utc)

    with SessionLocal() as db:
        with db.begin():
            statement = (
                select(ProcessingJob)
                .where(
                    ProcessingJob.id == job_id,
                    ProcessingJob.status == ProcessingJobStatus.RUNNING,
                    ProcessingJob.lease_token == lease_token,
                    ProcessingJob.locked_until > now,
                )
                .with_for_update()
            )

            job = db.scalars(statement).first()

            if job is None:
                return False

            job.last_error = str(error)[:1000]
            job.locked_until = None
            job.lease_token = None

            if job.attempt_count < MAX_ATTEMPTS:
                job.status = ProcessingJobStatus.PENDING
                job.finished_at = None

                delay_seconds = RETRY_DELAYS_SECONDS.get(
                    job.attempt_count,
                    30,
                )
                job.next_attempt_at = now + timedelta(seconds=delay_seconds)
            else:
                job.status = ProcessingJobStatus.FAILED
                job.finished_at = now
                job.next_attempt_at = None

    return True

def renew_lease_while_processing(
    job_id: uuid.UUID,
    lease_token: uuid.UUID,
    stop_event: threading.Event,
    lease_lost_event: threading.Event,
) -> None:
    while not stop_event.wait(LEASE_RENEW_INTERVAL.total_seconds()):
        try:
            renewed = renew_lease(job_id, lease_token)

            if not renewed:
                logger.warning(
                    "Lease lost for job %s",
                    job_id,
                )
                lease_lost_event.set()
                return

            logger.debug("Lease renewed for job %s", job_id)

        except Exception:
            logger.exception(
                "Lease renewal failed for job %s",
                job_id,
            )
            lease_lost_event.set()
            return
        
def is_document_ready(document_id: uuid.UUID) -> bool:
    with SessionLocal() as db:
        statement = select(Document.status).where(
            Document.id == document_id
        )

        status = db.scalar(statement)

        return status == DocumentStatus.READY
    
def process_claimed_job(
    job_id: uuid.UUID,
    lease_token: uuid.UUID,
) -> None:
    # Get the document ID while confirming this worker still owns the job.
    with SessionLocal() as db:
        statement = select(ProcessingJob.document_id).where(
            ProcessingJob.id == job_id,
            ProcessingJob.status == ProcessingJobStatus.RUNNING,
            ProcessingJob.lease_token == lease_token,
            ProcessingJob.locked_until > datetime.now(timezone.utc),
        )

        document_id = db.scalar(statement)

    if document_id is None:
        logger.warning(
            "Cannot process job %s: ownership was lost.",
            job_id,
        )
        return

    stop_event = threading.Event()
    lease_lost_event = threading.Event()

    renewal_thread = threading.Thread(
        target=renew_lease_while_processing,
        args=(
            job_id,
            lease_token,
            stop_event,
            lease_lost_event,
        ),
        name=f"lease-renewal-{job_id}",
        daemon=True,
    )

    renewal_thread.start()

    try:
        success = process_document(document_id)

        # Stop the renewal helper and wait for it to finish.
        stop_event.set()
        renewal_thread.join()

        if lease_lost_event.is_set():
            logger.warning(
                "Job %s finished processing, but ownership was lost. "
                "Skipping job-state updates.",
                job_id,
            )
            return

        if not success:
            fail_job(
                job_id,
                lease_token,
                RuntimeError(
                    "Document processing did not complete successfully."
                ),
            )
            return

        if not is_document_ready(document_id):
            fail_job(
                job_id,
                lease_token,
                RuntimeError(
                    "Processing returned success, but the document "
                    "is not READY."
                ),
            )
            return

        completed = complete_job(job_id, lease_token)

        if not completed:
            logger.warning(
                "Could not complete job %s: lease expired or ownership "
                "changed.",
                job_id,
            )
            return

        logger.info("Job %s completed successfully.", job_id)

    except Exception as error:
        stop_event.set()
        renewal_thread.join()

        if lease_lost_event.is_set():
            logger.warning(
                "Job %s raised an error after ownership was lost. "
                "Skipping failure update.",
                job_id,
            )
            return

        logger.exception("Job %s failed.", job_id)

        recorded = fail_job(job_id, lease_token, error)

        if not recorded:
            logger.warning(
                "Could not record failure for job %s because "
                "ownership may have changed.",
                job_id,
            )
            
def run_worker() -> None:
    logger.info("Juriqa processing worker started.")

    while True:
        try:
            claimed_job = claim_next_job()

            if claimed_job is None:
                time.sleep(WORKER_IDLE_INTERVAL)
                continue

            job_id, lease_token = claimed_job

            logger.info("Claimed job %s", job_id)

            process_claimed_job(job_id, lease_token)

        except Exception:
            logger.exception("Unexpected error in worker loop.")
            time.sleep(WORKER_IDLE_INTERVAL)