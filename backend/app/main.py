from fastapi import FastAPI

from backend.app.api.routes.documents import router as documents_router


app = FastAPI(
    title="Unthinkable Document Intelligence System",
    description="Self-verifying document summarization and analysis system",
    version="0.1.0"
)


app.include_router(documents_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "document-intelligence"
    }