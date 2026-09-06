from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from backend.app.api.routes.documents import router as documents_router
from backend.app.db.database import Base, engine
from backend.app.db import models


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Unthinkable Document Intelligence System",
    description="Self-verifying document summarization and analysis system",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(documents_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "document-intelligence"
    }