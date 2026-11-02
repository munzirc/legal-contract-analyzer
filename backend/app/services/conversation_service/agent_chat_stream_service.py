
import json
import logging
from collections.abc import Generator
from dataclasses import dataclass
from queue import Queue
from threading import Thread
from typing import Any
from uuid import UUID

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.exceptions.conversation_exceptions import ConversationNotFoundError
from app.models.conversation_models.conversation_model import Conversation
from app.models.document_model import Document
from app.schemas.agent_response_schema import AgentResponse
from app.schemas.chat import (
    ChatMessageResponse,
    ChatRequest,
)
from app.enums.chat_role import ChatRole
from app.models.conversation_models.chat_message_model import ChatMessage
from app.models.conversation_models.message_evidence_model import MessageEvidence
from app.models.conversation_models.evidence_region_model import EvidenceRegion
from app.schemas.input_schema import SelectedDocument
from app.services.agent_interaction_services.agent_service import start_agent
from app.services.conversation_service.sse_streaming.verify_agent_response import verify_agent_evidence_item

from app.services.conversation_service.validator.validate_conversation import (
    create_or_validate_conversation,
)

logger = logging.getLogger(__name__)

StreamEvent = tuple[str, dict[str, Any]]
EventQueue = Queue[StreamEvent | None]


@dataclass(frozen=True)
class StreamContext:
    conversation_id: UUID
    question: str
    document_ids: list[UUID]
    selected_documents: list[SelectedDocument]
    previous_interaction_id: str | None


def format_sse_event(event: str, data: dict[str, Any]) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


def prepare_stream_context(
    db: Session,
    request: ChatRequest,
) -> StreamContext:

    conversation, documents = create_or_validate_conversation(
        db=db,
        conversation_id=request.conversation_id,
        document_ids=request.document_ids,
        message=request.message
    )

    document_ids = [
        document.id
        for document in documents
    ]

    selected_documents = [
        SelectedDocument(
            document_id=document.id,
            filename=document.filename,
        )
        for document in documents
    ]


    return StreamContext(
        conversation_id=conversation.id,
        question=request.message,
        document_ids=document_ids,
        selected_documents=selected_documents,
        previous_interaction_id=conversation.last_interaction_id,
    )



def run_stream_worker(
    context: StreamContext,
    event_queue: EventQueue,
) -> None:
    conversation_id = str(context.conversation_id)

    try:
        with SessionLocal() as worker_db:

            conversation = worker_db.get(
                Conversation,
                context.conversation_id,
            )

            if conversation is None:
                raise ConversationNotFoundError(
                    f"Conversation {context.conversation_id} not found."
                )

            user_message = ChatMessage(
                conversation_id=conversation.id,
                role=ChatRole.USER,
                content=context.question,
            )

            worker_db.add(user_message)
            worker_db.commit()
            worker_db.refresh(user_message)

            # 1. Emit the saved user message.
            event_queue.put((
                "user_message",
                {
                    "conversation_id": conversation_id,
                    "message": {
                        "id": str(user_message.id),
                        "role": user_message.role.value,
                        "content": user_message.content,
                        "created_at": user_message.created_at.isoformat(),
                        "evidence": [],
                    },
                },
            ))

            # 2. Emit initial progress.
            event_queue.put((
                "progress",
                {
                    "conversation_id": conversation_id,
                    "message": "Starting contract analysis",
                },
            ))

            # 3. Run the agent.
            agent_result = start_agent(
                question=context.question,
                document_ids=context.document_ids,
                selected_documents=context.selected_documents,
                previous_interaction_id=context.previous_interaction_id,
                progress_callback=lambda message: event_queue.put(
                    (
                        "progress",
                        {
                            "conversation_id": conversation_id,
                            "message": message,
                        },
                    )
                ),
            )

            if (
                not agent_result.completed
                or agent_result.response is None
            ):
                event_queue.put((
                    "error",
                    {
                        "conversation_id": conversation_id,
                        "message": (
                            agent_result.error
                            or "The agent could not complete the analysis."
                        ),
                    },
                ))
                return

            agent_response: AgentResponse = agent_result.response

            conversation.last_interaction_id = (
                agent_result.interaction_id
            )

            assistant_message = ChatMessage(
                conversation_id=conversation.id,
                role=ChatRole.ASSISTANT,
                content=agent_response.answer,
            )

            worker_db.add(assistant_message)
            worker_db.commit()
            worker_db.refresh(assistant_message)

            # 4. Emit the saved assistant answer.
            answer_response = ChatMessageResponse(
                id=assistant_message.id,
                role=assistant_message.role,
                content=assistant_message.content,
                created_at=assistant_message.created_at,
                evidence=[],
            )

            event_queue.put((
                "answer",
                {
                    "conversation_id": conversation_id,
                    "message": answer_response.model_dump(mode="json"),
                },
            ))

            # 5. Load the selected documents.
            documents = worker_db.query(Document).filter(
                Document.id.in_(context.document_ids)
            ).all()

            documents_by_id = {
                document.id: document
                for document in documents
            }

            if len(documents_by_id) != len(set(context.document_ids)):
                raise ConversationNotFoundError(
                    "One or more documents attached to this conversation are no longer available."
                )

            total = len(agent_response.evidence)

            # 6. Verify and process evidence one item at a time.
            for index, evidence in enumerate(
                agent_response.evidence,
                start=1,
            ):
                event_queue.put((
                    "progress",
                    {
                        "conversation_id": conversation_id,
                        "message": f"Verifying evidence {index} of {total}",
                    },
                ))

                try:
                    evidence_document_id = UUID(
                        str(evidence.document_id)
                    )
                except (ValueError, TypeError, AttributeError):
                    evidence_document_id = None

                document = (
                    documents_by_id.get(evidence_document_id)
                    if evidence_document_id is not None
                    else None
                )

                if document is None:
                    continue

                verified = verify_agent_evidence_item(
                    db=worker_db,
                    evidence=evidence,
                    selected_documents=documents,
                )

                if verified is None:
                    continue

                verified_document = (
                    documents_by_id.get(verified.document_id)
                    if verified.document_id is not None
                    else None
                )

                if verified_document is None:
                    continue

                quote = verified.quote
                is_verified = verified.is_verified
                coordinates = verified.coordinates

                # 7. Persist evidence.
                evidence_record = MessageEvidence(
                    message_id=assistant_message.id,
                    document_id=verified_document.id,
                    quote=quote,
                    is_verified=is_verified,
                    regions=[
                        EvidenceRegion(
                            page_number=coordinate.page_number,
                            x1=coordinate.x1,
                            y1=coordinate.y1,
                            x2=coordinate.x2,
                            y2=coordinate.y2,
                        )
                        for coordinate in coordinates
                    ],
                )

                worker_db.add(evidence_record)
                worker_db.commit()
                worker_db.refresh(evidence_record)

                # 8. Emit evidence after persistence succeeds.
                evidence_data = {
                    "id": str(evidence_record.id),
                    "document_id": str(verified_document.id),
                    "filename": verified_document.filename,
                    "quote": quote,
                    "is_verified": is_verified,
                    "regions": [
                        {
                            "page_number": coordinate.page_number,
                            "x1": coordinate.x1,
                            "y1": coordinate.y1,
                            "x2": coordinate.x2,
                            "y2": coordinate.y2,
                        }
                        for coordinate in coordinates
                    ],
                }

                event_queue.put((
                    "evidence",
                    {
                        "conversation_id": conversation_id,
                        "message_id": str(assistant_message.id),
                        "evidence": evidence_data,
                        "index": index,
                        "total": total,
                    },
                ))

            # 9. All evidence items have been processed.
            event_queue.put((
                "complete",
                {
                    "conversation_id": conversation_id,
                    "user_message_id": str(user_message.id),
                    "assistant_message_id": str(assistant_message.id),
                    "status": "completed",
                },
            ))

    except Exception:
        logger.exception("Chat streaming worker failed.")

        event_queue.put((
            "error",
            {
                "conversation_id": conversation_id,
                "message": "An error occurred while processing your request.",
            },
        ))

    finally:
        event_queue.put(None)




def stream_chat_events(
    context: StreamContext,
) -> Generator[str, None, None]:
    event_queue: EventQueue = Queue()

    worker = Thread(
        target=run_stream_worker,
        args=(context, event_queue),
        daemon=True,
    )
    worker.start()

    while True:
        item: StreamEvent | None = event_queue.get()

        if item is None:
            break

        event_name, event_data = item
        yield format_sse_event(event_name, event_data)


def agent_chat_stream_service(
    db: Session,
    request: ChatRequest,
) -> StreamingResponse:
    # Validate before starting the response so ordinary validation errors
    # can still be returned as HTTP errors.
    context: StreamContext = prepare_stream_context(
        db=db,
        request=request,
    )

    return StreamingResponse(
        stream_chat_events(context),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
