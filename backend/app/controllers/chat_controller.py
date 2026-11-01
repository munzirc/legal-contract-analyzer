from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.exceptions.conversation_exceptions import (
    ConversationNotFoundError,
    ConversationHasNoDocumentsError,
    DocumentNotReadyError,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.conversation_service.agent_chat_service import agent_chat_service
from fastapi.responses import StreamingResponse

from app.services.conversation_service.agent_chat_stream_service import (
    agent_chat_stream_service,
)


def agent_chat_controller(
    db: Session,
    request: ChatRequest,
) -> ChatResponse:
    try:
        return agent_chat_service(
            db=db,
            request=request,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ConversationHasNoDocumentsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except DocumentNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
        
        

def agent_chat_stream_controller(
    db: Session,
    request: ChatRequest,
) -> StreamingResponse:
    try:
        return agent_chat_stream_service(
            db=db,
            request=request,
        )

    except ConversationNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ConversationHasNoDocumentsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except DocumentNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
