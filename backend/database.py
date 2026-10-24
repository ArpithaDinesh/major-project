import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from bson.objectid import ObjectId

logger = logging.getLogger("mindsync.database")

# Load .env file from project root or backend directory
root_env = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
if os.path.exists(root_env):
    load_dotenv(root_env)
else:
    load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "major_project")

# Global MongoDB Client & Database references
_mongo_client = None
_mongo_db = None
_is_connected_to_atlas = False


# ------------------------------------------------------------------------------
# Helpers: ObjectIds, Document Serialization & Category Mapping
# ------------------------------------------------------------------------------
VALID_CATEGORIES = [
    # 17 Standard Image & Document Classification Categories
    "bill",
    "receipt",
    "event_poster",
    "invitation",
    "ticket",
    "travel_booking",
    "identity_document",
    "certificate",
    "official_document",
    "handwritten_notes",
    "printed_notes",
    "screenshot",
    "menu_or_food_information",
    "product_or_label",
    "medical_document",
    "other",
    "unknown",
    # Legacy aliases
    "documents",
    "events",
    "travel",
    "food",
    "tickets",
    "receipts",
    "identity documents",
    "notes"
]

CATEGORY_MAPPING = {
    # Direct 17 categories
    "bill": "bill",
    "bills": "bill",
    "electricity_bill": "bill",
    "water_bill": "bill",
    "utility_bill": "bill",
    "receipt": "receipt",
    "receipts": "receipt",
    "event_poster": "event_poster",
    "event": "event_poster",
    "events": "event_poster",
    "poster": "event_poster",
    "invitation": "invitation",
    "invitations": "invitation",
    "ticket": "ticket",
    "tickets": "ticket",
    "travel_booking": "travel_booking",
    "travel": "travel_booking",
    "identity_document": "identity_document",
    "identity documents": "identity_document",
    "id_card": "identity_document",
    "passport": "identity_document",
    "certificate": "certificate",
    "certificates": "certificate",
    "official_document": "official_document",
    "documents": "official_document",
    "document": "official_document",
    "handwritten_notes": "handwritten_notes",
    "handwritten": "handwritten_notes",
    "printed_notes": "printed_notes",
    "notes": "printed_notes",
    "note": "printed_notes",
    "screenshot": "screenshot",
    "screenshots": "screenshot",
    "menu_or_food_information": "menu_or_food_information",
    "food_related": "menu_or_food_information",
    "food": "menu_or_food_information",
    "menu": "menu_or_food_information",
    "product_or_label": "product_or_label",
    "product": "product_or_label",
    "label": "product_or_label",
    "medical_document": "medical_document",
    "medical": "medical_document",
    "other": "other",
    "unknown": "unknown"
}


def normalize_category(cat: Optional[str]) -> str:
    """Normalize input category into one of the 17 categories without inventing values."""
    if not cat:
        return "other"
    clean = str(cat).strip().lower().replace("-", "_")
    if clean in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[clean]
    clean_space = clean.replace("_", " ")
    if clean_space in CATEGORY_MAPPING:
        return CATEGORY_MAPPING[clean_space]
    if clean in VALID_CATEGORIES:
        return clean
    return "other"


def to_object_id(val: Any) -> Optional[ObjectId]:
    """Safely convert string or ObjectId into ObjectId; returns None if invalid."""
    if isinstance(val, ObjectId):
        return val
    if not val:
        return None
    try:
        s = str(val).strip()
        if len(s) == 24:
            return ObjectId(s)
        return None
    except Exception:
        return None


def serialize_doc(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Serialize MongoDB document with ObjectIds and datetimes into JSON-safe dictionary."""
    if not doc:
        return None
    res = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            res[k] = str(v)
            if k == "_id":
                res["id"] = str(v)
        elif isinstance(v, datetime):
            res[k] = v.isoformat()
        elif isinstance(v, dict):
            res[k] = serialize_doc(v)
        elif isinstance(v, list):
            res[k] = [
                serialize_doc(i) if isinstance(i, dict)
                else (str(i) if isinstance(i, ObjectId)
                      else (i.isoformat() if isinstance(i, datetime) else i))
                for i in v
            ]
        else:
            res[k] = v
    if "_id" in res and "id" not in res:
        res["id"] = str(res["_id"])
    return res


# ------------------------------------------------------------------------------
# In-Memory Database Fallback (For offline / test runs)
# ------------------------------------------------------------------------------
class InMemoryCollection:
    """In-memory collection providing MongoDB-like interface when Atlas credentials are not yet entered."""
    def __init__(self, name: str):
        self.name = name
        self.docs: List[Dict[str, Any]] = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return "index_created"

    def count_documents(self, filter_q: Dict[str, Any] = None) -> int:
        if not filter_q:
            return len(self.docs)
        return len(list(self._filter_docs(filter_q)))

    def _matches(self, doc: Dict[str, Any], filter_q: Dict[str, Any]) -> bool:
        for k, v in filter_q.items():
            if k == "$or" and isinstance(v, list):
                if not any(self._matches(doc, cond) for cond in v):
                    return False
            elif isinstance(v, dict):
                val = doc.get(k)
                if "$regex" in v:
                    pattern = v["$regex"].lower()
                    if isinstance(val, list):
                        if not any(pattern in str(item).lower() for item in val):
                            return False
                    elif pattern not in str(val or "").lower():
                        return False
            else:
                # Compare value handling ObjectId <-> str equivalence
                doc_val = doc.get(k)
                if str(doc_val) != str(v) and doc_val != v:
                    return False
        return True

    def _filter_docs(self, filter_q: Dict[str, Any]):
        for doc in self.docs:
            if self._matches(doc, filter_q):
                yield doc

    def find(self, filter_q: Dict[str, Any] = None):
        filter_q = filter_q or {}
        matches = [dict(d) for d in self._filter_docs(filter_q)]

        class Cursor:
            def __init__(self, items):
                self.items = items

            def sort(self, field, direction=-1):
                reverse = direction == -1
                self.items.sort(key=lambda x: str(x.get(field, "")), reverse=reverse)
                return self

            def __iter__(self):
                return iter(self.items)

        return Cursor(matches)

    def find_one(self, filter_q: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for d in self._filter_docs(filter_q):
            return dict(d)
        return None

    def insert_one(self, doc: Dict[str, Any]):
        new_doc = dict(doc)
        if "_id" not in new_doc:
            new_doc["_id"] = ObjectId()
        if "id" not in new_doc:
            new_doc["id"] = str(new_doc["_id"])
        self.docs.append(new_doc)
        return type("InsertResult", (), {"inserted_id": new_doc["_id"]})

    def insert_many(self, docs: List[Dict[str, Any]]):
        for doc in docs:
            self.insert_one(doc)

    def update_one(self, filter_q: Dict[str, Any], update_doc: Dict[str, Any]):
        for doc in self.docs:
            if self._matches(doc, filter_q):
                if "$set" in update_doc:
                    doc.update(update_doc["$set"])
                return

    def delete_one(self, filter_q: Dict[str, Any]):
        for idx, doc in enumerate(self.docs):
            if self._matches(doc, filter_q):
                del self.docs[idx]
                return

    def delete_many(self, filter_q: Dict[str, Any]):
        self.docs = [d for d in self.docs if not self._matches(d, filter_q)]


class InMemoryDatabase:
    """Mock MongoDB Database wrapper with all 5 required collections."""
    def __init__(self):
        self.users = InMemoryCollection("users")
        self.files = InMemoryCollection("files")
        self.extracted_content = InMemoryCollection("extracted_content")
        self.metadata = InMemoryCollection("metadata")
        self.reminders = InMemoryCollection("reminders")
        self.items = InMemoryCollection("items")

    def __getitem__(self, name: str):
        return getattr(self, name, InMemoryCollection(name))


def get_db():
    """Retrieve connected MongoDB Atlas database, or fallback in-memory database."""
    global _mongo_client, _mongo_db, _is_connected_to_atlas
    if _mongo_db is not None:
        return _mongo_db

    # Check if a valid MongoDB Atlas URI is provided
    if MONGODB_URI and "<username>" not in MONGODB_URI and "<password>" not in MONGODB_URI:
        try:
            from pymongo import MongoClient
            _mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=4000)
            _mongo_db = _mongo_client[MONGODB_DB_NAME]
            _mongo_client.admin.command("ping")
            _is_connected_to_atlas = True
            print(f"[MongoDB Atlas] Successfully connected to cluster database: '{MONGODB_DB_NAME}'")
            return _mongo_db
        except Exception as e:
            print(f"[MongoDB Atlas] Connection attempt error: {e}. Running with in-memory database.")
            _mongo_db = InMemoryDatabase()
            _is_connected_to_atlas = False
            return _mongo_db
    else:
        # Placeholder credentials in .env
        print("[MongoDB Atlas] Placeholder detected in MONGODB_URI. Running in-memory MongoDB store.")
        _mongo_db = InMemoryDatabase()
        _is_connected_to_atlas = False
        return _mongo_db


def is_atlas_connected() -> bool:
    return _is_connected_to_atlas


# ------------------------------------------------------------------------------
# Collection Indexing & Setup (Requirement 3)
# ------------------------------------------------------------------------------
def setup_database_indexes(db):
    """
    Configure and enforce indexes across MongoDB Atlas collections:
    1. users: unique email, created_at
    2. files: user_id, upload_date, processing_status, compound (user_id, upload_date)
    3. extracted_content: file_id, user_id, compound (user_id, file_id)
    4. metadata: file_id, user_id, category, event_date, compound (user_id, category)
    5. reminders: user_id, file_id, reminder_datetime, status, compound (user_id, reminder_datetime)
    """
    try:
        # 1. users
        db.users.create_index([("email", 1)], unique=True)
        db.users.create_index([("created_at", -1)])

        # 2. files
        db.files.create_index([("user_id", 1)])
        db.files.create_index([("upload_date", -1)])
        db.files.create_index([("processing_status", 1)])
        db.files.create_index([("user_id", 1), ("upload_date", -1)])

        # 3. extracted_content
        db.extracted_content.create_index([("file_id", 1)])
        db.extracted_content.create_index([("user_id", 1)])
        db.extracted_content.create_index([("user_id", 1), ("file_id", 1)])

        # 4. metadata
        db.metadata.create_index([("file_id", 1)])
        db.metadata.create_index([("user_id", 1)])
        db.metadata.create_index([("category", 1)])
        db.metadata.create_index([("event_date", 1)])
        db.metadata.create_index([("user_id", 1), ("category", 1)])

        # 5. reminders
        db.reminders.create_index([("user_id", 1)])
        db.reminders.create_index([("file_id", 1)])
        db.reminders.create_index([("reminder_datetime", 1)])
        db.reminders.create_index([("status", 1)])
        db.reminders.create_index([("user_id", 1), ("reminder_datetime", 1)])

        # 6. items (user vault items isolation)
        db.items.create_index([("user_id", 1)])
        db.items.create_index([("ownerId", 1)])
        db.items.create_index([("user_id", 1), ("createdAt", -1)])

        # 7. embeddings (Atlas Vector Search & chunk filter)
        db.embeddings.create_index([("user_id", 1)])
        db.embeddings.create_index([("file_id", 1)])

        logger.info("[MongoDB Atlas] Indexes configured on users, files, extracted_content, metadata, reminders, items, and embeddings.")
    except Exception as e:
        logger.warning(f"[MongoDB Atlas] Index setup notice: {e}")


def init_db():
    """Initialize MongoDB collections, enforce schema indexes, and seed default records if empty."""
    db = get_db()
    
    # 1. Set up required indexes across all collections
    setup_database_indexes(db)

    # 2. Backfill created_at on any existing user documents if missing
    try:
        for u in db.users.find({"created_at": {"$exists": False}}):
            created_val = u.get("createdAt") or datetime.utcnow()
            if isinstance(created_val, str):
                try:
                    created_val = datetime.fromisoformat(created_val)
                except Exception:
                    created_val = datetime.utcnow()
            db.users.update_one({"_id": u["_id"]}, {"$set": {"created_at": created_val}})
    except Exception as e:
        logger.warning(f"User backfill notice: {e}")

    # 3. Try seeding if items collection is empty
    count = db.items.count_documents({})
    if count == 0:
        seed_default_data(db)


def seed_default_data(db):
    """Seed initial multi-modal items, reminders, and default user into MongoDB collections."""
    now = datetime.utcnow()

    initial_items = [
        {
            "id": "item-1",
            "title": "Distributed RAG System Architecture Guidelines",
            "type": "note",
            "category": "Architecture",
            "createdAt": (now - timedelta(hours=3)).isoformat(),
            "summary": "Detailed structural recommendations for building a sub-100ms retrieval pipeline with hybrid vector + lexical search and re-ranking models.",
            "content": """# Distributed RAG System Architecture Guidelines

### Core Principles
1. **Hybrid Retrieval**: Combine dense semantic embeddings (Cohere / OpenAI) with sparse BM25 indexing for domain-specific acronym precision.
2. **Context Compression**: Run cross-encoder reranking (e.g., bge-reranker-large) before passing top-5 chunks into the prompt context window to eliminate hallucination.
3. **Chunking Strategy**: Semantic boundary chunking at 450 tokens with 50-token overlapping sliding window.

### Cache Strategy
Store high-frequency prompt hashes in Redis with a 4-hour TTL to bypass LLM generation costs for common query patterns.""",
            "tags": ["RAG", "VectorDB", "FastAPI", "AI"],
            "entities": ["Hybrid Search", "BM25", "Redis Cache", "bge-reranker"],
            "detectedEvents": [
                {
                    "id": "ev-1",
                    "title": "Review vector indexing latency benchmarks",
                    "dueDate": (now + timedelta(days=2)).isoformat(),
                    "priority": "urgent",
                    "completed": False
                }
            ],
            "favorite": True,
            "duration": None,
            "audioUrl": None,
            "imageUrl": None,
            "url": None,
            "domain": None,
            "fileSize": None,
            "pages": None
        },
        {
            "id": "item-2",
            "title": "Client Product Discovery Memo - Mobile Offline First",
            "type": "voice",
            "category": "Product",
            "createdAt": (now - timedelta(hours=18)).isoformat(),
            "summary": "Audio recording detailing field feedback regarding service worker offline capability, background sync, and instant voice-to-text notes.",
            "content": "Transcription: 'The users specifically highlighted that during transit or low-connectivity zones, they need notes and voice memos to cache immediately onto local storage, then sync with the FastAPI backend once network is re-established. Let's make sure the PWA manifest and service worker handle this seamlessly.'",
            "tags": ["Mobile", "PWA", "OfflineSync", "VoiceMemo"],
            "entities": ["Service Worker", "IndexedDB", "FastAPI Sync", "Background Sync"],
            "detectedEvents": [
                {
                    "id": "ev-2",
                    "title": "PWA offline background sync review meeting",
                    "dueDate": (now + timedelta(days=4)).isoformat(),
                    "priority": "upcoming",
                    "completed": False
                }
            ],
            "favorite": False,
            "duration": "03:42",
            "audioUrl": None,
            "imageUrl": None,
            "url": None,
            "domain": None,
            "fileSize": None,
            "pages": None
        },
        {
            "id": "item-3",
            "title": "Cloud Infrastructure & Microservices Topology",
            "type": "image",
            "category": "DevOps",
            "createdAt": (now - timedelta(hours=36)).isoformat(),
            "summary": "Visual whiteboarding session diagram outlining Dockerized FastAPI services, Qdrant vector database, and MongoDB metadata stores.",
            "content": "Extracted OCR text: [API Gateway / Nginx Reverse Proxy] -> [FastAPI Application Cluster :8000] -> [Qdrant Vector Engine :6333] + [MongoDB Atlas :27017]. Backup snapshot scheduled daily at 02:00 UTC.",
            "tags": ["Docker", "Qdrant", "MongoDB", "DevOps"],
            "entities": ["Nginx", "FastAPI Cluster", "Qdrant Engine", "MongoDB Atlas"],
            "detectedEvents": [
                {
                    "id": "ev-3",
                    "title": "Deploy Qdrant cluster migration script",
                    "dueDate": (now + timedelta(hours=12)).isoformat(),
                    "priority": "urgent",
                    "completed": False
                }
            ],
            "favorite": True,
            "duration": None,
            "audioUrl": None,
            "imageUrl": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
            "url": None,
            "domain": None,
            "fileSize": None,
            "pages": None
        },
        {
            "id": "item-4",
            "title": "Deep Dive into Multi-Modal Reasoning 2026.pdf",
            "type": "document",
            "category": "Research",
            "createdAt": (now - timedelta(hours=72)).isoformat(),
            "summary": "Academic preprint discussing unified encoders for cross-modal indexing between speech phonemes, image embeddings, and technical literature.",
            "content": "Document Abstract: Recent advancements in multimodal LLMs demonstrate that cross-attention projection layers allow direct semantic alignment between Whisper acoustic tokens and ViT vision patches without intermediate transcription losses.",
            "tags": ["Multimodal", "Vision", "AudioTokens", "Whitepaper"],
            "entities": ["Whisper", "ViT", "Cross-Attention", "Phoneme Alignment"],
            "detectedEvents": [],
            "favorite": False,
            "duration": None,
            "audioUrl": None,
            "imageUrl": None,
            "url": None,
            "domain": None,
            "fileSize": "4.8 MB",
            "pages": 28
        },
        {
            "id": "item-5",
            "title": "FastAPI Documentation - High Performance Async APIs",
            "type": "link",
            "category": "Engineering",
            "createdAt": (now - timedelta(hours=96)).isoformat(),
            "summary": "Best practices for modular multi-file project layouts with APIRouter, dependency injection, and Pydantic v2 schemas.",
            "content": "FastAPI provides native asynchronous endpoints using Python 3.10+ async/await syntax, automatic OpenAPI interactive documentation, and Pydantic v2 validation achieving performance on par with NodeJS and Go.",
            "tags": ["FastAPI", "Python", "AsyncIO", "REST"],
            "entities": ["APIRouter", "Pydantic v2", "Uvicorn", "Starlette"],
            "detectedEvents": [],
            "favorite": False,
            "duration": None,
            "audioUrl": None,
            "imageUrl": None,
            "url": "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
            "domain": "fastapi.tiangolo.com",
            "fileSize": None,
            "pages": None
        }
    ]

    for item in initial_items:
        db.items.insert_one(item)
        for ev in item.get("detectedEvents", []):
            db.reminders.insert_one({
                "id": ev["id"],
                "title": ev["title"],
                "dueDate": ev["dueDate"],
                "priority": ev["priority"],
                "completed": ev.get("completed", False),
                "sourceId": item["id"],
                "sourceTitle": item["title"]
            })

    # Default User
    db.users.insert_one({
        "id": "usr-1",
        "name": "Alex Morgan",
        "email": "alex.morgan@mindsync.ai",
        "password_hash": "pbkdf2_sha256$mockhash$demopassword",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80",
        "plan": "Pro Knowledge Base",
        "storageUsed": "14.2 MB",
        "storageLimit": "5 GB",
        "privacyMode": "local-first"
    })
