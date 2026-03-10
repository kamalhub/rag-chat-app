"""
RAG Application Backend
========================
A FastAPI server that provides a RAG (Retrieval-Augmented Generation) pipeline
using LangChain, FAISS vector store, and OpenAI embeddings/LLM.
"""

import io
import os
import shutil
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from rag import RAGPipeline
from export_pdf import generate_chat_pdf
from mongodb_store import (
    store_document,
    list_documents,
    get_document,
    list_mortgage_application_ids,
    get_mortgage_application,
)

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
rag: RAGPipeline | None = None
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown logic."""
    global rag
    rag = RAGPipeline()
    yield


app = FastAPI(title="RAG Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    model: str | None = None  # e.g. gpt-4o-mini, gpt-4o


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


class IngestResponse(BaseModel):
    message: str
    num_chunks: int


class StatusResponse(BaseModel):
    status: str
    num_documents: int


class ModelsResponse(BaseModel):
    models: list[dict]  # [{"id": "gpt-4o-mini", "name": "..."}, ...]


class ExportMessage(BaseModel):
    role: str  # "user" or "assistant"
    text: str
    sources: list[dict] = []


class ExportRequest(BaseModel):
    messages: list[ExportMessage]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


# LLM models available for chat
AVAILABLE_MODELS = [
    {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "description": "Fast, cost-effective"},
    {"id": "gpt-4o", "name": "GPT-4o", "description": "Balanced performance"},
    {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "High capability"},
    {"id": "gpt-4o-2024-11-20", "name": "GPT-4o (Nov 2024)", "description": "Latest GPT-4o"},
    {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "description": "Strong reasoning, coding"},
    {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku", "description": "Fast, efficient"},
    {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Most capable"},
    {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "description": "Balanced performance"},
    {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "description": "Fast, lightweight"},
]


@app.get("/models", response_model=ModelsResponse)
async def models():
    """Return available LLM models for chat."""
    return ModelsResponse(models=AVAILABLE_MODELS)


@app.get("/documents")
async def documents_list():
    """List stored documents (from MongoDB). Returns [] if MongoDB not configured."""
    return {"documents": list_documents()}


@app.get("/documents/{filename:path}")
async def document_detail(filename: str):
    """Get full JSON data for a document by filename."""
    doc = get_document(filename)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@app.get("/mortgage-applications")
async def mortgage_applications_list():
    """List mortgage application document IDs for dropdown."""
    return {"applications": list_mortgage_application_ids()}


@app.get("/mortgage-applications/{document_id:path}")
async def mortgage_application_detail(document_id: str):
    """Get full mortgage application by documentID."""
    doc = get_mortgage_application(document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Mortgage application not found")
    return doc


@app.get("/status", response_model=StatusResponse)
async def status():
    """Return the current status of the vector store."""
    count = rag.document_count() if rag else 0
    return StatusResponse(status="ready" if count > 0 else "empty", num_documents=count)


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    """
    Upload a .txt, .md, .pdf, .docx, .png, .jpg, or .jpeg file, chunk it, embed it and add to the FAISS store.
    """
    if not file.filename.lower().endswith((".txt", ".md", ".pdf", ".docx", ".png", ".jpg", ".jpeg")):
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .md, .pdf, .docx, .png, .jpg, and .jpeg files are supported.",
        )

    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    num_chunks, chunks_data = rag.ingest(str(dest))
    store_document(file.filename, str(dest), chunks_data, num_chunks)
    return IngestResponse(message=f"Ingested {file.filename}", num_chunks=num_chunks)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message and get a RAG-augmented answer."""
    if rag.document_count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Upload a file first.")

    answer, sources = rag.query(req.message, model=req.model)
    return ChatResponse(answer=answer, sources=sources)


@app.post("/export")
async def export_chat(req: ExportRequest):
    """Export the chat conversation as a downloadable PDF."""
    if not req.messages:
        raise HTTPException(status_code=400, detail="No messages to export.")

    messages = [m.model_dump() for m in req.messages]
    pdf_bytes = generate_chat_pdf(messages)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"rag_chat_{timestamp}.pdf"

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
