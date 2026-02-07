"""
RAG Application Backend
========================
A FastAPI server that provides a RAG (Retrieval-Augmented Generation) pipeline
using LangChain, FAISS vector store, and OpenAI embeddings/LLM.
"""

import os
import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag import RAGPipeline

load_dotenv()

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


class ChatResponse(BaseModel):
    answer: str
    sources: list[dict]


class IngestResponse(BaseModel):
    message: str
    num_chunks: int


class StatusResponse(BaseModel):
    status: str
    num_documents: int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/status", response_model=StatusResponse)
async def status():
    """Return the current status of the vector store."""
    count = rag.document_count() if rag else 0
    return StatusResponse(status="ready" if count > 0 else "empty", num_documents=count)


@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)):
    """
    Upload a .txt, .md, or .pdf file, chunk it, embed it and add to the FAISS store.
    """
    if not file.filename.endswith((".txt", ".md", ".pdf")):
        raise HTTPException(status_code=400, detail="Only .txt, .md, and .pdf files are supported.")

    dest = UPLOAD_DIR / file.filename
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    num_chunks = rag.ingest(str(dest))
    return IngestResponse(message=f"Ingested {file.filename}", num_chunks=num_chunks)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send a message and get a RAG-augmented answer."""
    if rag.document_count() == 0:
        raise HTTPException(status_code=400, detail="No documents ingested yet. Upload a file first.")

    answer, sources = rag.query(req.message)
    return ChatResponse(answer=answer, sources=sources)
