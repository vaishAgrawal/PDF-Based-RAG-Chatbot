"""FastAPI application for document ingestion and question answering."""

import shutil
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from services.chunking import chunk_text
from services.embeddings import EmbeddingModel
from services.pdf_loader import extract_text_from_pdf
from services.rag_pipeline import RAGPipeline
from services.vector_store import VectorStore

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
VECTOR_DIR = BASE_DIR / "vector_db"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

embedder = EmbeddingModel()
store = VectorStore(VECTOR_DIR, embedder)
pipeline = RAGPipeline(store)
app = FastAPI(title="Document RAG API")


class Question(BaseModel):
    question: str
    document_id: str | None = None
    history: list[dict[str, str]] = []


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload")
def upload_document(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    destination = UPLOAD_DIR / Path(file.filename).name
    with destination.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    pages = extract_text_from_pdf(destination)
    text = "\n\n".join(page["text"] for page in pages)
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="The PDF contains no extractable text")
    document_id = uuid4().hex
    store.add(chunks, document_id)
    return {
        "document_id": document_id,
        "filename": destination.name,
        "chunks_indexed": len(chunks),
    }


@app.post("/ask")
def ask_question(payload: Question) -> dict:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    return pipeline.answer(question, payload.document_id, payload.history)
