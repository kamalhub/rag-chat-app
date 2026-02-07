"""
RAG Pipeline
=============
Encapsulates document loading, chunking, embedding, vector storage (FAISS),
and retrieval-augmented generation using LangChain.
"""

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


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


class RAGPipeline:
    """Manages the full RAG lifecycle: ingest → embed → retrieve → generate."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        k: int = 4,
    ):
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.llm = ChatOpenAI(model=model_name, temperature=0)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        self.k = k
        self.vectorstore: FAISS | None = None

    # ------------------------------------------------------------------
    # Ingest
    # ------------------------------------------------------------------
    def ingest(self, file_path: str) -> int:
        """Load a text file, split into chunks, embed and store in FAISS."""
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        chunks = self.splitter.split_documents(documents)

        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vectorstore.add_documents(chunks)

        return len(chunks)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------
    def query(self, question: str) -> tuple[str, list[dict]]:
        """Run a RAG query and return (answer, source_documents)."""
        if self.vectorstore is None:
            return "No documents have been ingested yet.", []

        chain = RetrievalQA.from_chain_type(
            llm=self.llm,
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
