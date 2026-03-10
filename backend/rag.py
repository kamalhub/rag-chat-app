"""
RAG Pipeline
=============
Encapsulates document loading, chunking, embedding, vector storage (FAISS),
and retrieval-augmented generation using LangChain.

Chunking strategy
-----------------
- **.md files** → Structure-aware: split on Markdown headers first, then apply
  semantic chunking within each section.
- **All other files** (.txt, .pdf, .docx) → Semantic chunking using embedding
  similarity to detect natural topic boundaries.
- A fixed-size fallback (`RecursiveCharacterTextSplitter`) is used when a
  document is too short for meaningful semantic splitting.
"""

from pathlib import Path

from langchain_community.document_loaders import TextLoader, PyPDFLoader, Docx2txtLoader
from langchain_core.documents import Document
from PIL import Image
import pytesseract
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.documents import Document

SYSTEM_TEMPLATE = """\
You are a helpful assistant that answers questions based on the provided context.
If you cannot find the answer in the context, say so honestly.
Always cite which part of the context you used.

Context:
{context}

Question: {question}

Answer:"""

QA_PROMPT = PromptTemplate(
    template=SYSTEM_TEMPLATE,
    input_variables=["context", "question"],
)

# Markdown headers to split on (structure-aware)
MD_HEADERS = [
    ("#", "heading_1"),
    ("##", "heading_2"),
    ("###", "heading_3"),
]

# Minimum character length for semantic chunking to be worthwhile.
# Shorter documents fall back to fixed-size splitting.
MIN_LENGTH_FOR_SEMANTIC = 200


class RAGPipeline:
    """Manages the full RAG lifecycle: ingest → embed → retrieve → generate."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        k: int = 4,
        breakpoint_threshold_type: str = "percentile",
    ):
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.llm = ChatOpenAI(model=model_name, temperature=0)

        # Semantic splitter — groups sentences by embedding similarity
        self.semantic_splitter = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type=breakpoint_threshold_type,
        )

        # Fixed-size fallback for very short documents
        self.fallback_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # Markdown structure-aware header splitter
        self.md_header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=MD_HEADERS,
        )

        self.k = k
        self.vectorstore: FAISS | None = None

    # ------------------------------------------------------------------
    # Chunking helpers
    # ------------------------------------------------------------------
    def _split_markdown(self, documents: list[Document]) -> list[Document]:
        """
        Structure-aware splitting for Markdown files.

        1. Split on headers (h1/h2/h3) to respect document structure.
        2. Apply semantic chunking within each section so that long
           sections are further divided at natural topic boundaries.
        """
        all_chunks: list[Document] = []

        for doc in documents:
            # Step 1 — split on headers
            header_chunks = self.md_header_splitter.split_text(doc.page_content)

            for hchunk in header_chunks:
                # Carry over original metadata + header metadata
                merged_meta = {**doc.metadata, **hchunk.metadata}

                if len(hchunk.page_content) >= MIN_LENGTH_FOR_SEMANTIC:
                    # Step 2 — semantic split within the section
                    sub_chunks = self.semantic_splitter.create_documents(
                        [hchunk.page_content],
                        metadatas=[merged_meta],
                    )
                    all_chunks.extend(sub_chunks)
                else:
                    all_chunks.append(
                        Document(page_content=hchunk.page_content, metadata=merged_meta)
                    )

        return all_chunks

    def _split_generic(self, documents: list[Document]) -> list[Document]:
        """
        Semantic chunking for non-Markdown files (.txt, .pdf, .docx).

        Falls back to fixed-size splitting if the document is too short
        for meaningful semantic boundaries.
        """
        total_length = sum(len(d.page_content) for d in documents)

        if total_length >= MIN_LENGTH_FOR_SEMANTIC:
            return self.semantic_splitter.split_documents(documents)
        else:
            return self.fallback_splitter.split_documents(documents)

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------
    def ingest(self, file_path: str) -> tuple[int, list[dict]]:
        """Load a text, PDF, or Word file, split into chunks, embed and store in FAISS.
        Returns (num_chunks, chunks_data) where chunks_data is JSON-serializable for storage."""
        ext = Path(file_path).suffix.lower()

        # --- Load ---
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
            documents = loader.load()
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
        elif ext in (".png", ".jpg", ".jpeg"):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            documents = [
                Document(
                    page_content=text.strip() or "No text could be extracted from this image.",
                    metadata={"source": file_path},
                )
            ]
        else:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()

        # --- Chunk ---
        if ext == ".md":
            chunks = self._split_markdown(documents)
        else:
            chunks = self._split_generic(documents)

        if not chunks:
            return 0, [], []

        # --- Embed & store ---
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vectorstore.add_documents(chunks)

        # Build JSON-serializable chunk data for optional MongoDB storage
        chunks_data = [
            {
                "content": c.page_content,
                "source": c.metadata.get("source", "unknown"),
                "metadata": {k: str(v) for k, v in c.metadata.items()},
            }
            for c in chunks
        ]
        return len(chunks), chunks_data

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def query(self, question: str, model: str | None = None) -> tuple[str, list[dict]]:
        """Run a RAG query and return (answer, source_documents)."""
        if self.vectorstore is None:
            return "No documents have been ingested yet.", []

        if model and model.startswith("claude-"):
            llm = ChatAnthropic(model=model, temperature=0)
        else:
            llm = ChatOpenAI(model=model, temperature=0) if model else self.llm
        chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": self.k}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": QA_PROMPT},
        )

        result = chain.invoke({"query": question})
        answer = result["result"]
        sources = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
            }
            for doc in result.get("source_documents", [])
        ]
        return answer, sources

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def document_count(self) -> int:
        if self.vectorstore is None:
            return 0
        return self.vectorstore.index.ntotal
