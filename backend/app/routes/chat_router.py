from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import StreamingResponse
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse

from app.controllers.chat_controller import (
    agent_chat_controller,
    agent_chat_stream_controller,
)


router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
def agent_chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    return agent_chat_controller(
        db=db,
        request=request,
    )
    
@router.post("/stream")
def agent_chat_stream(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> StreamingResponse:
    return agent_chat_stream_controller(
        db=db,
        request=request,
    )