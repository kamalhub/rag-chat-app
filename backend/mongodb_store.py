"""
MongoDB document store.

Persists ingested document data in JSON format when MONGODB_URI is set.
Each uploaded document is stored as a single document with metadata and chunks.
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from pymongo import MongoClient
    from pymongo.errors import PyMongoError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False


COLLECTION = "documents"
MORTGAGE_COLLECTION = "Mortgage Application"


def _get_client():
    """Return MongoDB client if configured, else None."""
    uri = os.getenv("MONGODB_URI", "").strip()
    if not uri:
        return None
    if not PYMONGO_AVAILABLE:
        return None
    try:
        return MongoClient(uri, serverSelectionTimeoutMS=5000)
    except Exception:
        return None


def store_document(
    filename: str,
    file_path: str,
    chunks: list[dict],
    num_chunks: int,
) -> bool:
    """
    Store document data in MongoDB as JSON-friendly structure.

    Args:
        filename: Original filename
        file_path: Full path to the uploaded file
        chunks: List of {"content": str, "source": str, "metadata": dict}
        num_chunks: Number of chunks

    Returns:
        True if stored successfully, False otherwise
    """
    client = _get_client()
    if client is None:
        return False

    try:
        db = client.get_default_database()
        if db is None:
            db = client["rag"]
        col = db[COLLECTION]

        # Build JSON-serializable document
        doc = {
            "filename": filename,
            "file_path": str(file_path),
            "file_type": Path(file_path).suffix.lower(),
            "num_chunks": num_chunks,
            "chunks": chunks,
            "ingested_at": datetime.now(datetime.UTC).isoformat(),
        }

        col.insert_one(doc)
        return True
    except PyMongoError:
        return False
    finally:
        client.close()


def list_documents() -> list[dict]:
    """Return list of stored documents (filename, num_chunks, ingested_at)."""
    client = _get_client()
    if client is None:
        return []

    try:
        db = client.get_default_database()
        if db is None:
            db = client["rag"]
        col = db[COLLECTION]
        cursor = col.find(
            {},
            {"filename": 1, "num_chunks": 1, "ingested_at": 1, "_id": 0},
        ).sort("ingested_at", -1)
        return list(cursor)
    except PyMongoError:
        return []
    finally:
        client.close()


def get_document(filename: str) -> dict | None:
    """Return full document data by filename (latest if re-uploaded)."""
    client = _get_client()
    if client is None:
        return None

    try:
        db = client.get_default_database()
        if db is None:
            db = client["rag"]
        col = db[COLLECTION]
        doc = col.find_one(
            {"filename": filename},
            {"_id": 0},
            sort=[("ingested_at", -1)],
        )
        return doc
    except PyMongoError:
        return None
    finally:
        client.close()


def list_mortgage_application_ids() -> list[dict]:
    """Return list of mortgage applications with documentID and display label."""
    client = _get_client()
    if client is None:
        return []

    try:
        db = client.get_default_database()
        if db is None:
            db = client["rag"]
        col = db[MORTGAGE_COLLECTION]
        cursor = col.find(
            {},
            {"documentID": 1, "applicants": 1, "status": 1, "_id": 0},
        ).sort("created_at", -1)
        result = []
        for doc in cursor:
            doc_id = doc.get("documentID", "")
            applicants = doc.get("applicants", [])
            names = ""
            if applicants:
                parts = [
                    f"{a.get('forenames', '')} {a.get('surname', '')}".strip()
                    for a in applicants[:2]
                ]
                names = " & ".join(p for p in parts if p)
            label = f"{doc_id} ({names})" if names else doc_id
            result.append({"documentID": doc_id, "label": label})
        return result
    except PyMongoError:
        return []
    finally:
        client.close()


def get_mortgage_application(document_id: str) -> dict | None:
    """Return full mortgage application by documentID."""
    client = _get_client()
    if client is None:
        return None

    try:
        db = client.get_default_database()
        if db is None:
            db = client["rag"]
        col = db[MORTGAGE_COLLECTION]
        doc = col.find_one({"documentID": document_id}, {"_id": 0})
        return doc
    except PyMongoError:
        return None
    finally:
        client.close()


def is_configured() -> bool:
    """Return True if MongoDB is configured and available."""
    return _get_client() is not None
