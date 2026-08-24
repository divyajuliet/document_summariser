from fastapi import FastAPI

app = FastAPI(
    title="Unthinkable Document Intelligence System",
    description="Self-verifying document summarization and analysis system",
    version="0.1.0"
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "document-intelligence"
    }