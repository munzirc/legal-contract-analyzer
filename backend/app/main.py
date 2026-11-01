
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.logging_config import configure_logging
from app.routes.document_route import router as document_router
from app.routes.conversation_router import router as conversation_router 
from app.routes.chat_router import router as chat_router
from app.routes.processing_progress import router as progress_router
from app.routes.document_pdf_router import router as pdf_router
from app.exceptions.exception_handlers import register_exception_handlers



configure_logging()

app = FastAPI(
    title="Legal Contract Analyzer API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(document_router)
app.include_router(conversation_router)
app.include_router(chat_router)
app.include_router(progress_router)
app.include_router(pdf_router)


@app.get("/")
def root():
    return {
        "message": "Legal Contract Analyzer API is running"
    }
    