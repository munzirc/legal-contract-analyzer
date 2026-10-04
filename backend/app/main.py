from fastapi import FastAPI

from app.routes.document_route import router as document_router

app = FastAPI(
    title="Legal Contract Analyzer API",
    version="1.0.0"
)

app.include_router(document_router)


@app.get("/")
def root():
    return {
        "message": "Legal Contract Analyzer API is running"
    }
    