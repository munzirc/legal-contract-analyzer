from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.conversation_exceptions import (
    AgentResponseError,
    ConversationNotFoundError,
    ConversationHasNoDocumentsError,
    DocumentNotReadyError,
    DocumentNotFoundError,
    ConversationDocumentNotFoundError,
)


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(AgentResponseError)
    async def agent_response_error_handler(
        request: Request,
        exc: AgentResponseError,
    ):
        return JSONResponse(
            status_code=502,
            content={"detail": exc.message},
        )

    @app.exception_handler(ConversationNotFoundError)
    async def conversation_not_found_handler(
        request: Request,
        exc: ConversationNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc) or "Conversation not found."},
        )

    @app.exception_handler(ConversationHasNoDocumentsError)
    async def conversation_has_no_documents_handler(
        request: Request,
        exc: ConversationHasNoDocumentsError,
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": str(exc) or "This conversation has no associated documents."
            },
        )

    @app.exception_handler(DocumentNotReadyError)
    async def document_not_ready_handler(
        request: Request,
        exc: DocumentNotReadyError,
    ):
        return JSONResponse(
            status_code=409,
            content={
                "detail": str(exc) or "An associated document is not ready for analysis."
            },
        )

    @app.exception_handler(DocumentNotFoundError)
    async def document_not_found_handler(
        request: Request,
        exc: DocumentNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc) or "Document not found."},
        )

    @app.exception_handler(ConversationDocumentNotFoundError)
    async def conversation_document_not_found_handler(
        request: Request,
        exc: ConversationDocumentNotFoundError,
    ):
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(exc)
                or "The document is not associated with this conversation."
            },
        )