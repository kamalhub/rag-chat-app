# RAG Chat Application

A simple Retrieval-Augmented Generation (RAG) application with a **Python/LangChain** backend and a **Next.js/React** chat frontend.

Upload `.txt`, `.md`, or `.pdf` documents, and then ask questions — the app retrieves relevant chunks and generates grounded answers using OpenAI.

---

## Architecture

```
┌──────────────┐        HTTP        ┌───────────────────┐
│  Next.js UI  │  ◄──────────────►  │  FastAPI Backend   │
│  (React)     │   /chat  /ingest   │  LangChain + FAISS │
└──────────────┘                    └───────────────────┘
```

**Backend stack:** FastAPI, LangChain, FAISS (vector store), OpenAI (embeddings + LLM)

**Frontend stack:** Next.js 15, React 19, TypeScript, CSS Modules

---

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Node.js 20+
- An OpenAI API key

---

## Quick Start

### 1. Backend

```bash
cd backend

# Set your OpenAI key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Install dependencies and run the server (uv handles the venv automatically)
uv run uvicorn main:app --reload --port 8000
```

> `uv run` creates a `.venv`, installs all dependencies from `pyproject.toml`, and launches the command — all in one step.

The API will be available at `http://localhost:8000`. Check `http://localhost:8000/docs` for the interactive Swagger UI.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run the dev server
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## Usage

1. **Upload a document** — Click the upload area in the sidebar and select a `.txt`, `.md`, or `.pdf` file. A sample file (`sample_data.txt`) is included in the backend folder.
2. **Ask questions** — Type a question in the chat input and press Enter or click Send.
3. **View sources** — Expandable source cards appear below each answer showing the retrieved context chunks.

---

## API Endpoints

| Method | Path      | Description                        |
|--------|-----------|------------------------------------|
| GET    | `/health` | Health check                       |
| GET    | `/status` | Returns vector store document count|
| POST   | `/ingest` | Upload and ingest a `.txt`/`.md`/`.pdf` |
| POST   | `/chat`   | Send a message and get a RAG answer|

---

## Project Structure

```
rag-app/
├── backend/
│   ├── main.py              # FastAPI app & routes
│   ├── rag.py               # RAG pipeline (ingest, query)
│   ├── pyproject.toml
│   ├── .env.example
│   └── sample_data.txt      # Sample document about RAG
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app router
│   │   ├── components/      # React components
│   │   └── lib/api.ts       # API client
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

---

## Configuration

| Variable               | Default                  | Description           |
|------------------------|--------------------------|-----------------------|
| `OPENAI_API_KEY`       | (required)               | Your OpenAI API key   |
| `NEXT_PUBLIC_API_URL`  | `http://localhost:8000`  | Backend URL for the UI|

---

## Extending This Example

Some ideas for next steps:

- **Persist the vector store** — save/load FAISS index to disk
- **Conversation memory** — add `ConversationBufferMemory` for multi-turn chat
- **Streaming responses** — use FastAPI `StreamingResponse` + SSE on the frontend
- **Authentication** — protect the API with JWT or API keys
- **Deploy** — Dockerize both services, or deploy the frontend on Vercel and the backend on Railway/Fly.io
