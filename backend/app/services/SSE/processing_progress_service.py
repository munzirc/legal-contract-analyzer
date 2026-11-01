from datetime import datetime


def build_progress_payload(
    row: dict,
    now: datetime,
) -> dict:
    
    document_status = row["document_status"].name
    job_status = row["job_status"].name

    valid_lease = (
        job_status == "RUNNING"
        and row["locked_until"] is not None
        and row["locked_until"] > now
    )

    payload = {
        "document_id": str(row["document_id"]),
        "document_status": document_status,
        "status": "processing",
        "stage": "preparing",
        "message": "Preparing Document",
        "is_currently_processing": valid_lease,
    }

    if document_status == "READY":
        payload.update(
            status="ready",
            stage="ready",
            message="Document Ready",
            is_currently_processing=False,
        )
        return payload

    if document_status == "REJECTED":
        payload.update(
            status="rejected",
            stage="finished",
            message="Document Rejected",
            is_currently_processing=False,
        )
        return payload

    if job_status == "FAILED":
        payload.update(
            status="failed",
            stage="finished",
            message="Processing Failed",
            is_currently_processing=False,
        )
        return payload

    if job_status == "COMPLETED":
        payload.update(
            status="failed",
            stage="finished",
            message="Processing Failed",
            is_currently_processing=False,
        )
        return payload

    if job_status == "PENDING":
        if (
            row["next_attempt_at"] is not None
            and row["next_attempt_at"] > now
        ):
            payload.update(
                status="waiting_retry",
                stage="waiting",
                message="Retry Scheduled",
                is_currently_processing=False,
            )
        else:
            payload.update(
                status="queued",
                stage="waiting",
                message="Waiting in Queue",
                is_currently_processing=False,
            )

        return payload

    # A RUNNING job with an expired lease may need to be reclaimed.
    if not valid_lease:
        payload.update(
            status="queued",
            stage="waiting",
            message="Waiting to Resume",
            is_currently_processing=False,
        )
        return payload

    stage_messages = {
        "UPLOADED": ("queued", "Document Queued"),
        "EXTRACTING": ("extracting", "Extracting Document"),
        "VALIDATING": ("analyzing", "Analyzing Document"),
        "STRUCTURE_DETECTION_FAILED": (
            "retrying",
            "Retrying Document Analysis",
        ),
        "CHUNKING": ("organizing", "Organizing Document"),
        "CHUNKING_FAILED": (
            "retrying",
            "Retrying Document Processing",
        ),
        "EMBEDDING_PIECES": ("preparing", "Preparing Document"),
        "EMBEDDING_PIECES_FAILED": (
            "retrying",
            "Retrying Document Preparation",
        ),
        "EMBEDDING": ("processing", "Processing Document"),
        "EMBEDDING_FAILED": (
            "retrying",
            "Retrying Document Processing",
        ),
        "EXTRACTION_FAILED": (
            "retrying",
            "Retrying Document Extraction",
        ),
    }

    stage, message = stage_messages.get(
        document_status,
        ("preparing", "Preparing Document"),
    )

    payload.update(
        stage=stage,
        message=message,
    )

    return payload


def has_progress_changed(
    previous_payload: dict | None,
    current_payload: dict,
) -> bool:
    
    return previous_payload != current_payload
