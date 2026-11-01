from uuid import UUID
from sqlalchemy.orm import Session


from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.services.conversation_service.validator.validate_conversation import validate_conversation
from app.models.conversation_models.conversation_model import Conversation
from app.exceptions.conversation_exceptions import AgentResponseError
from app.schemas.input_schema import SelectedDocument
from app.services.agent_interaction_services.agent_service import start_agent
from app.exceptions.conversation_exceptions import (ConversationNotFoundError, )
from app.services.conversation_service.quote_verification.verify_agent_response import verify_agent_response_evidence
from app.services.conversation_service.save_messages.save_chat_messages import persist_chat_turn




def agent_chat_service(
    db: Session,
    request: ChatRequest,
) -> ChatResponse:
    
    conversation_id = request.conversation_id

    conversation: Conversation | None = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is None:
        raise ConversationNotFoundError(
            f"Conversation {conversation_id} not found."
        )

    _, selected_documents = validate_conversation(
        db=db,
        conversation_id=conversation_id,
    )

    document_ids: list[UUID] = [
        document.id for document in selected_documents
    ]

    agent_documents: list[SelectedDocument] = [
        SelectedDocument(
            document_id=document.id,
            filename=document.filename,
        )
        for document in selected_documents
    ]

    agent_result = start_agent(
        question=request.message,
        document_ids=document_ids,
        selected_documents=agent_documents,
        previous_interaction_id=conversation.last_interaction_id,
        progress_callback=lambda message: print(
            f"[PROGRESS] {message}"
        )
    )
    

    if not agent_result.completed or agent_result.response is None:
        raise AgentResponseError(
            "Juriqa couldn't generate an answer right now. Please try again."
        )
    
    conversation.last_interaction_id = agent_result.interaction_id

    verified_result = verify_agent_response_evidence(
        db=db,
        agent_response=agent_result.response,
        selected_documents=selected_documents,
    )

    user_message, assistant_message = persist_chat_turn(
        db=db,
        conversation_id=conversation_id,
        user_question=request.message,
        assistant_answer=agent_result.response.answer,
        verified_result=verified_result,
    )

    print("\n========== PERSISTED CHAT TURN ==========")
    print(f"User message ID: {user_message.id}")
    print(f"Assistant message ID: {assistant_message.id}")
    print(f"Verified evidence count: {len(assistant_message.evidences)}")


    return ChatResponse(
        conversation_id=conversation_id,
        messages=[
            ChatMessageResponse(
                id=user_message.id,
                role=user_message.role,
                content=user_message.content,
                created_at=user_message.created_at,
                evidence=[],
            ),
            ChatMessageResponse(
                id=assistant_message.id,
                role=assistant_message.role,
                content=assistant_message.content,
                created_at=assistant_message.created_at,
                evidence=[],
            ),
        ],
    )

    
    
    
