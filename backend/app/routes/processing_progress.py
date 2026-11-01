
import asyncio
import json
import time
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.repositories.processing_progress_repository import (
    ACTIVE_JOB_STATUSES,
    get_progress_rows,
)
from app.services.SSE.processing_progress_service import (
    build_progress_payload,
    has_progress_changed,
)


router = APIRouter(tags=["processing"])

POLL_INTERVAL_SECONDS = 1
HEARTBEAT_INTERVAL_SECONDS = 15


def format_sse(event_name: str, data: dict) -> str:
    """Format a server-sent event."""

    return (
        f"event: {event_name}\n"
        f"data: {json.dumps(data)}\n\n"
    )


@router.get("/api/processing/progress")
async def stream_processing_progress(request: Request):
    async def event_stream():
        tracked_job_ids: set[UUID] = set()
        last_payloads: dict[UUID, dict] = {}
        last_heartbeat = time.monotonic()

        while True:
            if await request.is_disconnected():
                return

            now = datetime.now(timezone.utc)

            rows = await asyncio.to_thread(
                get_progress_rows,
                set(tracked_job_ids),
            )

            returned_job_ids = {
                row["job_id"]
                for row in rows
            }

            # Remove jobs that were deleted while the stream was open.
            missing_job_ids = tracked_job_ids - returned_job_ids

            for job_id in missing_job_ids:
                tracked_job_ids.discard(job_id)
                last_payloads.pop(job_id, None)

            active_job_ids = {
                row["job_id"]
                for row in rows
                if row["job_status"] in ACTIVE_JOB_STATUSES
            }

            for row in rows:
                job_id = row["job_id"]

                payload = build_progress_payload(row, now)
                previous_payload = last_payloads.get(job_id)

                if has_progress_changed(previous_payload, payload):
                    yield format_sse("document_progress", payload)
                    last_payloads[job_id] = payload

                if row["job_status"] in ACTIVE_JOB_STATUSES:
                    tracked_job_ids.add(job_id)
                else:
                    tracked_job_ids.discard(job_id)
                    last_payloads.pop(job_id, None)

            # Finish the stream when no active or tracked jobs remain.
            if not active_job_ids and not tracked_job_ids:
                yield format_sse(
                    "queue_idle",
                    {
                        "message": "All document processing jobs have finished."
                    },
                )
                return

            if (
                time.monotonic() - last_heartbeat
                >= HEARTBEAT_INTERVAL_SECONDS
            ):
                yield ": heartbeat\n\n"
                last_heartbeat = time.monotonic()

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
