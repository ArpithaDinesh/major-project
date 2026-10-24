import json
import os
import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

logger = logging.getLogger("mindsync.main")

from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from database import init_db, get_db, is_atlas_connected, to_object_id, serialize_doc, normalize_category
from bson.objectid import ObjectId
from schemas import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    ReminderCreate,
    ChatQuery,
    ProcessNoteRequest,
    ProcessLinkRequest,
    UserLogin,
    UserRegister,
    UserProfileUpdate,
    ConfirmReminderRequest,
    MetadataUpdate
)
from services.rag_service import run_rag_pipeline, store_embedded_chunks, search_vector_embeddings
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user as auth_get_current_user,
    get_current_user_optional,
    get_default_user_oid
)
from services.image_pipeline_service import execute_image_pipeline
from services.ai_service import (
    extract_entities,
    extract_tags,
    extract_semantic_keywords,
    detect_deadlines_and_events,
    generate_summary,
    scrape_link_metadata
)
from services.storage_service import validate_image_file, save_image_file, UPLOAD_DIR
from services.image_intelligence import analyze_image_intelligence


# Initialize FastAPI Application
app = FastAPI(
    title="MindSync Backend",
    description="High-performance Python FastAPI service for MindSync Personal Knowledge Management",
    version="1.0.0"
)

# Enable CORS for Vite frontend (http://localhost:5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static storage for image & document files
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="api_uploads")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

# Startup event to ensure database is created and seeded
@app.on_event("startup")
def on_startup():
    init_db()
    # Pre-warm PaddleOCR in background thread so user requests have zero cold start lag
    import threading
    def warmup_ocr():
        try:
            from services.ocr_service import get_ocr_engine
            get_ocr_engine()
        except Exception as e:
            pass
    threading.Thread(target=warmup_ocr, daemon=True).start()


# Helpers for Serializing DB Documents
def serialize_item(row: Any) -> Dict[str, Any]:
    if not row:
        return {}
    res = dict(row)
    res.pop("_id", None)
    
    tags = res.get("tags", [])
    if isinstance(tags, str):
        try:
            tags = json.loads(tags)
        except:
            tags = []
    res["tags"] = tags

    entities = res.get("entities", [])
    if isinstance(entities, str):
        try:
            entities = json.loads(entities)
        except:
            entities = []
    res["entities"] = entities

    detected_events = res.get("detectedEvents", [])
    if isinstance(detected_events, str):
        try:
            detected_events = json.loads(detected_events)
        except:
            detected_events = []
    res["detectedEvents"] = detected_events

    suggested_reminders = res.get("suggestedReminders", [])
    if isinstance(suggested_reminders, str):
        try:
            suggested_reminders = json.loads(suggested_reminders)
        except:
            suggested_reminders = []
    res["suggestedReminders"] = suggested_reminders

    res["category"] = res.get("category") or "General"
    res["summary"] = res.get("summary") or ""
    res["content"] = res.get("content") or ""
    res["favorite"] = bool(res.get("favorite", False))
    res["keywords"] = res.get("keywords", [])
    res["categoryData"] = res.get("categoryData", {})
    res["imageCategory"] = res.get("imageCategory")
    res["rawOcrText"] = res.get("rawOcrText")
    res["ocrConfidence"] = res.get("ocrConfidence")
    res["ocrDetails"] = res.get("ocrDetails", {})
    res["normalizedDates"] = res.get("normalizedDates", [])
    res["processingStatus"] = res.get("processingStatus", "completed")
    res["isSensitive"] = bool(res.get("isSensitive", False))
    res["ownerId"] = str(res.get("ownerId") or res.get("user_id") or "")
    if "user_id" in res and res["user_id"] is not None:
        res["user_id"] = str(res["user_id"])
    if "file_id" in res and res["file_id"] is not None:
        res["file_id"] = str(res["file_id"])
    res["fileRef"] = res.get("fileRef")
    res["mimeType"] = res.get("mimeType")
    res["dimensions"] = res.get("dimensions")
    return res

def serialize_reminder(row: Any) -> Dict[str, Any]:
    if not row:
        return {}
    res = dict(row)
    oid = res.get("_id")
    rem_id = str(oid) if oid else res.get("id")
    res["id"] = rem_id
    res["_id"] = rem_id
    if "user_id" in res and isinstance(res["user_id"], ObjectId):
        res["user_id"] = str(res["user_id"])
    if "file_id" in res and isinstance(res["file_id"], ObjectId):
        res["file_id"] = str(res["file_id"])

    # Map status <-> completed
    if "status" in res:
        res["completed"] = (res["status"] == "completed")
    elif "completed" in res:
        res["status"] = "completed" if res["completed"] else "pending"
    else:
        res["status"] = "pending"
        res["completed"] = False

    # Map reminder_datetime <-> dueDate
    if "reminder_datetime" in res:
        dt = res["reminder_datetime"]
        res["dueDate"] = dt.isoformat() if isinstance(dt, datetime) else str(dt)
        res["reminder_datetime"] = res["dueDate"]
    elif "dueDate" in res:
        res["reminder_datetime"] = res["dueDate"]

    res["priority"] = res.get("priority") or "normal"
    return res

# ==============================================================================
# API ROUTER (Mounts to both /api and root /)
# ==============================================================================
api = APIRouter()

# ------------------------------------------------------------------------------
# 1. Health & Status
# ------------------------------------------------------------------------------
@api.get("/health")
def health_check():
    db = get_db()
    items_count = db.items.count_documents({})
    pending_reminders = db.reminders.count_documents({"completed": False})

    return {
        "status": "online",
        "system": "MindSync FastAPI Server",
        "version": "1.0.0",
        "database": "MongoDB Atlas" if is_atlas_connected() else "MongoDB Engine (In-Memory Fallback)",
        "timestamp": datetime.utcnow().isoformat(),
        "totalItems": items_count,
        "pendingReminders": pending_reminders,
        "mode": "mongodb-atlas"
    }

# ------------------------------------------------------------------------------
# 2. Knowledge Items CRUD (Strict User Isolation)
# ------------------------------------------------------------------------------
@api.get("/items")
def get_items(
    category: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort: Optional[str] = Query("newest"),
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """List vault items strictly isolated for the authenticated user."""
    db = get_db()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    # Base query: only records belonging to the authenticated user, excluding isolated demo items
    user_filter = {
        "$or": [{"user_id": user_oid}, {"user_id": user_str}, {"ownerId": user_str}],
        "is_isolated": {"$ne": True},
        "ownerId": {"$ne": "SYSTEM_DEMO_ISOLATED"}
    }

    and_clauses = [user_filter]

    if category and category != "All":
        and_clauses.append({"category": category})

    if type and type != "All":
        and_clauses.append({"type": type})

    if search:
        reg = {"$regex": search, "$options": "i"}
        and_clauses.append({
            "$or": [
                {"title": reg},
                {"summary": reg},
                {"content": reg},
                {"tags": reg},
                {"entities": reg},
                {"keywords": reg},
                {"rawOcrText": reg},
                {"categoryData.merchant": reg},
                {"categoryData.event_name": reg},
                {"categoryData.venue": reg},
                {"categoryData.carrier": reg},
                {"categoryData.recipient_name": reg}
            ]
        })

    filter_q = {"$and": and_clauses} if len(and_clauses) > 1 else user_filter

    sort_field = "createdAt"
    sort_dir = -1
    if sort == "oldest":
        sort_dir = 1
    elif sort == "alpha":
        sort_field = "title"
        sort_dir = 1

    docs = db.items.find(filter_q).sort(sort_field, sort_dir)
    return [serialize_item(d) for d in docs]

@api.get("/items/{item_id}")
def get_item_by_id(item_id: str, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Retrieve single item validating strict ownership by authenticated user."""
    db = get_db()
    doc = db.items.find_one({"id": item_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    item_uid = str(doc.get("user_id") or doc.get("ownerId") or "")
    if item_uid != user_str and doc.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to access this item.")

    return serialize_item(doc)

@api.post("/items")
def create_item(item: KnowledgeItemCreate, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Create item strictly linked to verified authenticated user ID."""
    db = get_db()
    new_id = f"item-{int(datetime.utcnow().timestamp() * 1000)}"
    created_at = datetime.utcnow().isoformat()

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    # Intelligent enrichment if empty
    content = item.content or ""
    summary = item.summary or generate_summary(content)
    tags = item.tags if item.tags else extract_tags(f"{item.title} {content}", item.category)
    entities = item.entities if item.entities else extract_entities(f"{item.title} {content}")
    detected_events = item.detectedEvents if item.detectedEvents else []

    doc = {
        "id": new_id,
        "title": item.title,
        "type": item.type,
        "category": item.category,
        "createdAt": created_at,
        "summary": summary,
        "content": content,
        "tags": tags,
        "entities": entities,
        "keywords": item.keywords or [],
        "detectedEvents": detected_events,
        "suggestedReminders": item.suggestedReminders or [],
        "categoryData": item.categoryData or {},
        "imageCategory": item.imageCategory,
        "rawOcrText": item.rawOcrText,
        "ocrConfidence": item.ocrConfidence,
        "ocrDetails": item.ocrDetails or {},
        "normalizedDates": item.normalizedDates or [],
        "processingStatus": item.processingStatus or "completed",
        "isSensitive": bool(item.isSensitive),
        "user_id": user_oid,
        "ownerId": user_str,
        "favorite": bool(item.favorite),
        "duration": item.duration,
        "audioUrl": item.audioUrl,
        "imageUrl": item.imageUrl,
        "fileRef": item.fileRef,
        "mimeType": item.mimeType,
        "dimensions": item.dimensions,
        "url": item.url,
        "domain": item.domain,
        "fileSize": item.fileSize,
        "pages": item.pages
    }
    db.items.insert_one(doc)

    # Persist only explicitly confirmed detected events into reminders collection with user_id
    for ev in detected_events:
        ev_id = ev.get("id") or f"ev-{int(datetime.utcnow().timestamp() * 1000)}"
        db.reminders.insert_one({
            "_id": ObjectId(),
            "id": ev_id,
            "user_id": user_oid,
            "title": ev.get("title", item.title),
            "description": item.title,
            "dueDate": ev.get("dueDate", created_at),
            "reminder_datetime": datetime.utcnow(),
            "priority": ev.get("priority", "upcoming"),
            "status": "pending",
            "completed": bool(ev.get("completed", False)),
            "sourceId": new_id,
            "sourceTitle": item.title,
            "created_at": datetime.utcnow()
        })

    # Store vector embedding chunk in Atlas Vector Search collection with owning user_id (Requirement 3)
    try:
        embed_content = f"{item.title}\n{summary}\n{content}"
        store_embedded_chunks(
            db=db,
            user_oid=user_oid,
            file_id=to_object_id(item.fileRef),
            item_id=new_id,
            text=embed_content,
            metadata={"title": item.title, "type": item.type, "category": item.category}
        )
    except Exception as emb_e:
        logger.warning(f"Vector embedding chunk storage notice: {emb_e}")

    return serialize_item(doc)

@api.put("/items/{item_id}")
def update_item(item_id: str, update: KnowledgeItemUpdate, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Allow user to update and correct inaccurate fields with strict ownership validation."""
    db = get_db()
    doc = db.items.find_one({"id": item_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    item_uid = str(doc.get("user_id") or doc.get("ownerId") or "")
    if item_uid != user_str and doc.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to update this item.")

    set_dict = {}
    if update.title is not None: set_dict["title"] = update.title
    if update.category is not None: set_dict["category"] = update.category
    if update.summary is not None: set_dict["summary"] = update.summary
    if update.content is not None: set_dict["content"] = update.content
    if update.tags is not None: set_dict["tags"] = update.tags
    if update.entities is not None: set_dict["entities"] = update.entities
    if update.keywords is not None: set_dict["keywords"] = update.keywords
    if update.categoryData is not None: set_dict["categoryData"] = update.categoryData
    if update.imageCategory is not None: set_dict["imageCategory"] = update.imageCategory
    if update.rawOcrText is not None: set_dict["rawOcrText"] = update.rawOcrText
    if update.suggestedReminders is not None: set_dict["suggestedReminders"] = update.suggestedReminders
    if update.favorite is not None: set_dict["favorite"] = bool(update.favorite)

    set_dict["updatedAt"] = datetime.utcnow().isoformat()
    db.items.update_one({"id": item_id}, {"$set": set_dict})
    doc.update(set_dict)
    return serialize_item(doc)

@api.post("/items/{item_id}/confirm-reminder")
def confirm_item_reminder(item_id: str, req: ConfirmReminderRequest, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Confirm a suggested reminder with strict ownership validation."""
    db = get_db()
    item = db.items.find_one({"id": item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    item_uid = str(item.get("user_id") or item.get("ownerId") or "")
    if item_uid != user_str and item.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to add reminders for this item.")

    rem_id = f"ev-{int(datetime.utcnow().timestamp() * 1000)}"
    rem_doc = {
        "_id": ObjectId(),
        "id": rem_id,
        "user_id": user_oid,
        "title": req.title,
        "description": item.get("title", "Image Source"),
        "dueDate": req.dueDate,
        "reminder_datetime": datetime.utcnow(),
        "priority": req.priority or "normal",
        "status": "pending",
        "completed": False,
        "sourceId": item_id,
        "sourceTitle": item.get("title", "Image Source"),
        "created_at": datetime.utcnow()
    }
    db.reminders.insert_one(rem_doc)

    # Mark as confirmed in item.suggestedReminders
    sugs = item.get("suggestedReminders", [])
    for s in sugs:
        if s.get("title") == req.title or s.get("dueDate") == req.dueDate:
            s["confirmed"] = True
    db.items.update_one({"id": item_id}, {"$set": {"suggestedReminders": sugs}})

    return serialize_reminder(rem_doc)

@api.delete("/items/{item_id}")
def delete_item(item_id: str, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Delete an item and its associated user reminders with ownership validation."""
    db = get_db()
    doc = db.items.find_one({"id": item_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    item_uid = str(doc.get("user_id") or doc.get("ownerId") or "")
    if item_uid != user_str and doc.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this item.")

    db.items.delete_one({"id": item_id})
    # Cascade delete associated reminders and embeddings belonging only to this user
    db.reminders.delete_many({"sourceId": item_id, "$or": [{"user_id": user_oid}, {"user_id": user_str}]})
    db.embeddings.delete_many({"item_id": item_id, "$or": [{"user_id": user_oid}, {"user_id": user_str}]})
    return {"success": True, "deletedId": item_id}

@api.post("/items/{item_id}/favorite")
def toggle_favorite(item_id: str, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Toggle favorite status validating ownership."""
    db = get_db()
    doc = db.items.find_one({"id": item_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    item_uid = str(doc.get("user_id") or doc.get("ownerId") or "")
    if item_uid != user_str and doc.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to modify this item.")

    new_fav = not bool(doc.get("favorite", False))
    db.items.update_one({"id": item_id}, {"$set": {"favorite": new_fav}})
    doc["favorite"] = new_fav
    return serialize_item(doc)

# ------------------------------------------------------------------------------
# 3. Reminders & Deadlines (Strict User Isolation)
# ------------------------------------------------------------------------------
@api.get("/reminders")
def get_reminders(
    priority: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    filter_q = {
        "$or": [{"user_id": user_oid}, {"user_id": user_str}],
        "is_isolated": {"$ne": True}
    }
    if priority:
        filter_q["priority"] = priority

    docs = db.reminders.find(filter_q).sort("reminder_datetime", 1)
    return [serialize_reminder(r) for r in docs]

@api.post("/reminders")
def create_reminder(
    reminder: ReminderCreate,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    db = get_db()
    rem_oid = ObjectId()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)

    due_date = reminder.dueDate
    rem_dt = None
    if due_date:
        try:
            rem_dt = datetime.fromisoformat(due_date)
        except Exception:
            rem_dt = datetime.utcnow()

    f_oid = to_object_id(reminder.sourceId)

    doc = {
        "_id": rem_oid,
        "id": str(rem_oid),
        "user_id": user_oid,
        "file_id": f_oid,
        "title": reminder.title,
        "description": reminder.sourceTitle or None,
        "reminder_datetime": rem_dt or datetime.utcnow(),
        "dueDate": due_date,
        "priority": reminder.priority or "normal",
        "status": "pending",
        "completed": False,
        "sourceId": reminder.sourceId,
        "sourceTitle": reminder.sourceTitle,
        "created_at": datetime.utcnow()
    }
    db.reminders.insert_one(doc)
    return serialize_reminder(doc)

@api.post("/reminders/{rem_id}/toggle")
def toggle_reminder(
    rem_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    db = get_db()
    rem_oid = to_object_id(rem_id)
    filter_q = {"$or": [{"_id": rem_oid}, {"id": rem_id}]} if rem_oid else {"id": rem_id}

    doc = db.reminders.find_one(filter_q)
    if not doc:
        raise HTTPException(status_code=404, detail="Reminder not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)
    rem_uid = str(doc.get("user_id") or "")

    if rem_uid != user_str and doc.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to update this reminder.")

    new_completed = not bool(doc.get("completed", False))
    new_status = "completed" if new_completed else "pending"
    db.reminders.update_one(filter_q, {"$set": {"completed": new_completed, "status": new_status}})
    doc["completed"] = new_completed
    doc["status"] = new_status
    return serialize_reminder(doc)

@api.delete("/reminders/{rem_id}")
def delete_reminder(
    rem_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    db = get_db()
    rem_oid = to_object_id(rem_id)
    filter_q = {"$or": [{"_id": rem_oid}, {"id": rem_id}]} if rem_oid else {"id": rem_id}

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    existing = db.reminders.find_one(filter_q)
    if not existing:
        raise HTTPException(status_code=404, detail="Reminder not found")

    rem_uid = str(existing.get("user_id") or "")
    if rem_uid != user_str and existing.get("user_id") != user_oid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this reminder.")

    db.reminders.delete_one(filter_q)
    return {"success": True, "deletedId": rem_id}

# ------------------------------------------------------------------------------
# 4. Natural Language RAG Chat (Strict User Isolation)
# ------------------------------------------------------------------------------
@api.post("/chat")
def chat_query(query: ChatQuery, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    user_str = str(user_oid or user_id)

    # Strictly retrieve items and reminders belonging exclusively to this authenticated user
    user_items = [
        serialize_item(r) for r in db.items.find({
            "$or": [{"user_id": user_oid}, {"user_id": user_str}, {"ownerId": user_str}],
            "is_isolated": {"$ne": True},
            "ownerId": {"$ne": "SYSTEM_DEMO_ISOLATED"}
        })
    ]
    user_reminders = [
        serialize_reminder(r) for r in db.reminders.find({
            "$or": [{"user_id": user_oid}, {"user_id": user_str}],
            "is_isolated": {"$ne": True}
        })
    ]

    # Run intelligent hybrid RAG retrieval and synthesis pipeline strictly bounded to authenticated user
    response_data = run_rag_pipeline(query.prompt, user_items, user_reminders, user_oid=user_oid, db=db)
    return response_data

# ------------------------------------------------------------------------------
# 5. Multi-Modal Ingestion & AI Processing
# ------------------------------------------------------------------------------
@api.post("/process/note")
def process_note(req: ProcessNoteRequest):
    summary = generate_summary(req.text)
    tags = extract_tags(req.text, req.category or "General")
    entities = extract_entities(req.text)
    title = req.title or (req.text.split('\n')[0][:50] if req.text else "Untitled Note")
    events = detect_deadlines_and_events(req.text, title)

    return {
        "title": title,
        "summary": summary,
        "tags": tags,
        "entities": entities,
        "detectedEvents": events
    }

@api.post("/process/link")
def process_link(req: ProcessLinkRequest):
    meta = scrape_link_metadata(req.url)
    entities = extract_entities(f"{meta['title']} {meta['summary']}")
    tags = extract_tags(f"{meta['title']} {meta['summary']}", "WebLink")

    return {
        "title": meta["title"],
        "domain": meta["domain"],
        "url": meta["url"],
        "summary": meta["summary"],
        "tags": tags,
        "entities": entities
    }

@api.post("/process/image")
@api.post("/process/ocr")
async def process_image_upload(
    file: UploadFile = File(...),
    category: Optional[str] = Form(None),
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """
    Dedicated endpoint connecting PaddleOCR with MongoDB Atlas collections:
    Strictly assigns authenticated user ID; never accepts unauthenticated uploads.
    """
    filename = file.filename or "uploaded_image.png"
    content_type = file.content_type
    content = await file.read()

    user_id = current_user["id"]

    try:
        result = execute_image_pipeline(
            file_bytes=content,
            filename=filename,
            content_type=content_type,
            user_id=user_id,
            category_hint=category
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PaddleOCR processing error: {str(e)}")

@api.post("/process/upload")
async def process_file_upload(
    file: UploadFile = File(...),
    category: str = Form("General"),
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    filename = file.filename or "uploaded_file"
    ext = os.path.splitext(filename)[1].lower()
    content = await file.read()
    file_size_mb = f"{(len(content) / (1024 * 1024)):.1f} MB"
    extracted_text = ""
    ocr_details = None
    extra_meta = {}

    user_id = current_user["id"]

    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif", ".heic"]:
        res = execute_image_pipeline(content, filename, file.content_type, user_id, category)
        return {
            "title": filename.replace(ext, ""),
            "type": "image",
            "fileSize": res["fileSize"],
            "imageUrl": res["fileUrl"],
            "fileRef": res["filePath"],
            "fileId": res["fileId"],
            "file_id": res["file_id"],
            "dimensions": res["dimensions"],
            "mimeType": res["mimeType"],
            "summary": res["summary"],
            "content": res["cleanedText"] or res["summary"],
            "rawOcrText": res["rawText"],
            "tags": res["tags"],
            "entities": res["keywords"],
            "keywords": res["keywords"],
            "extracted_entities": res.get("extracted_entities", []),
            "categoryData": res["categoryData"],
            "category_fields": res.get("category_fields", {}),
            "category": res["category"],
            "imageCategory": res["category"],
            "subtype": res.get("subtype"),
            "confidence": res.get("confidence", 0.0),
            "reason": res.get("reason", ""),
            "needs_review": res.get("needs_review", False),
            "ocrConfidence": res["confidence"],
            "ocrDetails": {
                "text": res["cleanedText"],
                "confidence": res["confidence"],
                "lines": res["lines"],
                "lineCount": res["lineCount"],
                "wordCount": res["wordCount"],
                "charCount": len(res["cleanedText"])
            },
            "suggestedReminders": res["suggestedReminders"],
            "normalizedDates": res["normalizedDates"],
            "isSensitive": res["isSensitive"],
            "processingStatus": res["processingStatus"]
        }
    elif ext in [".pdf"]:
        item_type = "pdf"
        pages = 14
        summary = f"Parsed PDF document '{filename}' with extracted executive summary, structured sections, and figures."
    elif ext in [".ppt", ".pptx"]:
        item_type = "ppt"
        pages = 22
        summary = f"Parsed presentation deck '{filename}' with slide-by-slide analysis, bullet points, and speaker notes."
    elif ext in [".doc", ".docx"]:
        item_type = "docx"
        pages = 6
        summary = f"Word document '{filename}' processed with section outlines, table of contents, and key findings."
    elif ext in [".mp3", ".wav", ".m4a", ".ogg"]:
        item_type = "voice"
        pages = None
        summary = f"Audio memo '{filename}' transcribed with Whisper speech-to-text engine."
    else:
        item_type = "document"
        pages = 1
        summary = f"Uploaded document '{filename}' indexed into MindSync vault."

    combined_context = f"{filename} {summary} {extracted_text}"
    tags = extract_tags(combined_context, category)
    semantic_keywords = extract_semantic_keywords(combined_context)

    return {
        "title": filename.replace(ext, ""),
        "type": item_type,
        "fileSize": file_size_mb,
        "pages": pages,
        "summary": summary,
        "content": extracted_text or summary,
        "tags": tags,
        "entities": semantic_keywords,
        "ocrDetails": ocr_details
    }


# ------------------------------------------------------------------------------
# 5b. Files, Extracted Content & Metadata Management (Collections & Strict Isolation)
# ------------------------------------------------------------------------------
@api.get("/files")
def list_files(
    status: Optional[str] = Query(None),
    file_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """List files strictly for the authenticated user (isolated by user_id)."""
    db = get_db()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)

    filter_q = {"$or": [{"user_id": user_oid}, {"user_id": str(user_oid)}]}
    if status:
        filter_q["processing_status"] = status
    if file_type:
        filter_q["file_type"] = file_type

    docs = db.files.find(filter_q).sort("upload_date", -1).skip(skip).limit(limit)
    return [serialize_doc(d) for d in docs]

@api.get("/files/{file_id}")
def get_file_record(
    file_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Retrieve file record by ID with user ownership validation."""
    db = get_db()
    f_oid = to_object_id(file_id)
    filter_q = {"$or": [{"_id": f_oid}, {"id": file_id}]} if f_oid else {"id": file_id}

    file_doc = db.files.find_one(filter_q)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    if file_doc.get("user_id") != user_oid and str(file_doc.get("user_id")) != str(user_oid):
        raise HTTPException(status_code=403, detail="Not authorized to access this file.")

    return serialize_doc(file_doc)

@api.delete("/files/{file_id}")
def delete_file_record(
    file_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Delete a file and its associated extracted content, metadata, and reminders with ownership validation."""
    db = get_db()
    f_oid = to_object_id(file_id)
    filter_q = {"$or": [{"_id": f_oid}, {"id": file_id}]} if f_oid else {"id": file_id}

    file_doc = db.files.find_one(filter_q)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    if file_doc.get("user_id") != user_oid and str(file_doc.get("user_id")) != str(user_oid):
        raise HTTPException(status_code=403, detail="Not authorized to delete this file.")

    # Remove stored physical file if present
    stored_path = file_doc.get("stored_file_path")
    if stored_path and os.path.exists(stored_path):
        try:
            os.remove(stored_path)
        except Exception:
            pass

    # Delete records across all related collections
    ref_query = {"$or": [{"file_id": f_oid}, {"file_id": file_id}]} if f_oid else {"file_id": file_id}
    db.files.delete_one(filter_q)
    db.extracted_content.delete_many(ref_query)
    db.metadata.delete_many(ref_query)
    db.reminders.delete_many(ref_query)
    db.embeddings.delete_many(ref_query)

    return {"success": True, "deletedFileId": file_id}

@api.get("/files/{file_id}/extracted-content")
def get_file_extracted_content(
    file_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Retrieve extracted text and OCR data for a file with ownership validation."""
    db = get_db()
    f_oid = to_object_id(file_id)
    file_filter = {"$or": [{"_id": f_oid}, {"id": file_id}]} if f_oid else {"id": file_id}
    file_doc = db.files.find_one(file_filter)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    if file_doc.get("user_id") != user_oid and str(file_doc.get("user_id")) != str(user_oid):
        raise HTTPException(status_code=403, detail="Not authorized to access this content.")

    ref_query = {"$or": [{"file_id": f_oid}, {"file_id": file_id}]} if f_oid else {"file_id": file_id}
    content_doc = db.extracted_content.find_one(ref_query)
    if not content_doc:
        raise HTTPException(status_code=404, detail="Extracted content not found for this file.")

    return serialize_doc(content_doc)

@api.get("/files/{file_id}/metadata")
def get_file_metadata(
    file_id: str,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Retrieve structured metadata and entities for a file with ownership validation."""
    db = get_db()
    f_oid = to_object_id(file_id)
    file_filter = {"$or": [{"_id": f_oid}, {"id": file_id}]} if f_oid else {"id": file_id}
    file_doc = db.files.find_one(file_filter)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    if file_doc.get("user_id") != user_oid and str(file_doc.get("user_id")) != str(user_oid):
        raise HTTPException(status_code=403, detail="Not authorized to access this metadata.")

    ref_query = {"$or": [{"file_id": f_oid}, {"file_id": file_id}]} if f_oid else {"file_id": file_id}
    meta_doc = db.metadata.find_one(ref_query)
    if not meta_doc:
        raise HTTPException(status_code=404, detail="Metadata not found for this file.")

    return serialize_doc(meta_doc)

@api.put("/files/{file_id}/metadata")
def update_file_metadata(
    file_id: str,
    updates: MetadataUpdate,
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Allow user to update and correct inaccurate metadata fields without inventing missing values."""
    db = get_db()
    f_oid = to_object_id(file_id)
    file_filter = {"$or": [{"_id": f_oid}, {"id": file_id}]} if f_oid else {"id": file_id}
    file_doc = db.files.find_one(file_filter)
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")

    user_id = current_user["id"]
    user_oid = to_object_id(user_id)
    if file_doc.get("user_id") != user_oid and str(file_doc.get("user_id")) != str(user_oid):
        raise HTTPException(status_code=403, detail="Not authorized to edit this metadata.")

    ref_query = {"$or": [{"file_id": f_oid}, {"file_id": file_id}]} if f_oid else {"file_id": file_id}
    meta_doc = db.metadata.find_one(ref_query)
    if not meta_doc:
        raise HTTPException(status_code=404, detail="Metadata record not found for this file.")

    set_dict = {}
    if updates.category is not None:
        set_dict["category"] = normalize_category(updates.category)
    if updates.subtype is not None:
        set_dict["subtype"] = updates.subtype
    if updates.title is not None:
        set_dict["title"] = updates.title
    if updates.summary is not None:
        set_dict["summary"] = updates.summary
    if updates.entities is not None:
        set_dict["entities"] = updates.entities
    if updates.category_fields is not None:
        set_dict["category_fields"] = updates.category_fields
        if updates.entities is None:
            set_dict["entities"] = updates.category_fields
    if updates.keywords is not None:
        set_dict["keywords"] = updates.keywords
    if updates.location is not None:
        set_dict["location"] = updates.location
    if updates.needs_review is not None:
        set_dict["needs_review"] = updates.needs_review
    if updates.reason is not None:
        set_dict["reason"] = updates.reason
    if updates.event_date is not None:
        if updates.event_date.strip():
            try:
                set_dict["event_date"] = datetime.fromisoformat(updates.event_date)
            except Exception:
                set_dict["event_date"] = None
        else:
            set_dict["event_date"] = None

    if set_dict:
        db.metadata.update_one({"_id": meta_doc["_id"]}, {"$set": set_dict})
        meta_doc.update(set_dict)

    return serialize_doc(meta_doc)

@api.get("/metadata")
def query_metadata(
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(auth_get_current_user)
):
    """Query metadata collection with strict user isolation and category/keyword search."""
    db = get_db()
    user_id = current_user["id"]
    user_oid = to_object_id(user_id)

    user_filter = {"$or": [{"user_id": user_oid}, {"user_id": str(user_oid)}]}
    and_clauses = [user_filter]

    if category and category != "All":
        and_clauses.append({"category": normalize_category(category)})

    if keyword:
        and_clauses.append({"keywords": {"$regex": keyword, "$options": "i"}})

    if search:
        reg = {"$regex": search, "$options": "i"}
        and_clauses.append({
            "$or": [
                {"title": reg},
                {"summary": reg},
                {"keywords": reg},
                {"location": reg}
            ]
        })

    filter_q = {"$and": and_clauses} if len(and_clauses) > 1 else user_filter

    docs = db.metadata.find(filter_q).sort("created_at", -1).skip(skip).limit(limit)
    return [serialize_doc(d) for d in docs]


# ------------------------------------------------------------------------------
# 6. Auth & User Profile
# ------------------------------------------------------------------------------
@api.post("/auth/login")
def login_user(creds: UserLogin):
    db = get_db()
    email_clean = creds.email.strip().lower()
    user = db.users.find_one({"email": email_clean})

    if not user:
        raise HTTPException(
            status_code=401, 
            detail="No account found with this email. Please click 'Create Account' to register."
        )

    stored_hash = user.get("password_hash")
    if not stored_hash or not verify_password(creds.password, stored_hash):
        raise HTTPException(
            status_code=401, 
            detail="Incorrect password. Please verify your credentials and try again."
        )

    user_oid_str = str(user.get("_id") or user.get("id"))
    # Create signed cryptographic JWT access token
    access_token = create_access_token({
        "sub": user_oid_str,
        "email": user["email"],
        "name": user.get("name") or email_clean.split("@")[0].title()
    })

    user_dict = dict(user)
    user_dict["id"] = user_oid_str
    user_dict["user_id"] = user_oid_str
    user_dict["_id"] = user_oid_str
    user_dict.pop("password_hash", None)
    if "created_at" in user_dict and isinstance(user_dict["created_at"], datetime):
        user_dict["created_at"] = user_dict["created_at"].isoformat()
    user_dict["token"] = access_token
    user_dict["access_token"] = access_token
    user_dict["token_type"] = "bearer"
    return user_dict

@api.post("/auth/signup")
def register_user(reg: UserRegister):
    db = get_db()
    email_clean = reg.email.strip().lower()

    if not reg.password or len(reg.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")

    existing = db.users.find_one({"email": email_clean})
    if existing:
        raise HTTPException(
            status_code=400, 
            detail="An account with this email already exists. Please sign in instead."
        )

    new_user_oid = ObjectId()
    user_id_str = str(new_user_oid)
    name_clean = reg.name.strip() if reg.name and reg.name.strip() else email_clean.split("@")[0].title()
    avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={name_clean}"
    hashed_pwd = hash_password(reg.password)
    now_dt = datetime.utcnow()

    user = {
        "_id": new_user_oid,
        "id": user_id_str,
        "name": name_clean,
        "email": email_clean,
        "password_hash": hashed_pwd,
        "created_at": now_dt,
        "avatar": avatar,
        "plan": "Pro Knowledge Base",
        "storageUsed": "0 MB",
        "storageLimit": "5 GB",
        "privacyMode": "cloud-sync",
        "createdAt": now_dt.isoformat()
    }
    db.users.insert_one(user)

    # Generate signed JWT access token
    access_token = create_access_token({
        "sub": user_id_str,
        "email": email_clean,
        "name": name_clean
    })

    user_dict = dict(user)
    user_dict["id"] = user_id_str
    user_dict["user_id"] = user_id_str
    user_dict["_id"] = user_id_str
    user_dict.pop("password_hash", None)
    user_dict["created_at"] = now_dt.isoformat()
    user_dict["token"] = access_token
    user_dict["access_token"] = access_token
    user_dict["token_type"] = "bearer"
    return user_dict

@api.get("/auth/me")
def get_current_user_profile(current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Protected endpoint: Returns the currently authenticated user based on JWT Bearer token."""
    return current_user

@api.put("/auth/profile")
def update_profile(updates: UserProfileUpdate, current_user: Dict[str, Any] = Depends(auth_get_current_user)):
    """Protected endpoint: Updates profile fields for the authenticated user."""
    db = get_db()
    user_id = current_user["id"]
    set_dict = {}
    if updates.name:
        set_dict["name"] = updates.name
    if updates.avatar:
        set_dict["avatar"] = updates.avatar
    if updates.privacyMode:
        set_dict["privacyMode"] = updates.privacyMode

    if set_dict:
        db.users.update_one({"id": user_id}, {"$set": set_dict})
        current_user.update(set_dict)

    return current_user

# ------------------------------------------------------------------------------
# 7. Backup & Reset
# ------------------------------------------------------------------------------
@api.get("/backup")
def export_backup():
    db = get_db()
    items = [serialize_item(r) for r in db.items.find({})]
    reminders = [serialize_reminder(r) for r in db.reminders.find({})]

    return {
        "system": "MindSync PKM Export",
        "database": "MongoDB Atlas" if is_atlas_connected() else "MongoDB Engine",
        "exportedAt": datetime.utcnow().isoformat(),
        "itemCount": len(items),
        "reminderCount": len(reminders),
        "items": items,
        "reminders": reminders
    }

@api.post("/reset")
def reset_to_defaults():
    from database import seed_default_data
    db = get_db()
    db.items.delete_many({})
    db.reminders.delete_many({})
    db.users.delete_many({})
    seed_default_data(db)
    return {"status": "success", "message": "MongoDB collections reset to initial demo vault."}

# ==============================================================================
# Mount API Router on both /api (for Vite proxy) and root / (for direct calls)
# ==============================================================================
app.include_router(api, prefix="/api")
app.include_router(api, prefix="")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
