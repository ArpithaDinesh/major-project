from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict
from datetime import datetime

# ==========================================
# 1. Knowledge Item Schemas
# ==========================================
class DetectedEvent(BaseModel):
    id: Optional[str] = None
    title: str
    dueDate: str
    priority: str = "normal"
    completed: bool = False

class KnowledgeItemCreate(BaseModel):
    title: str
    type: str
    category: str = "General"
    summary: Optional[str] = ""
    content: Optional[str] = ""
    tags: List[str] = []
    entities: List[str] = []
    keywords: Optional[List[str]] = []
    detectedEvents: List[Dict[str, Any]] = []
    suggestedReminders: Optional[List[Dict[str, Any]]] = []
    categoryData: Optional[Dict[str, Any]] = None
    category_fields: Optional[Dict[str, Any]] = None
    subtype: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    needs_review: Optional[bool] = False
    imageCategory: Optional[str] = None
    rawOcrText: Optional[str] = None
    ocrConfidence: Optional[float] = None
    ocrDetails: Optional[Dict[str, Any]] = None
    normalizedDates: Optional[List[Dict[str, Any]]] = []
    processingStatus: Optional[str] = "completed"
    isSensitive: Optional[bool] = False
    ownerId: Optional[str] = None
    duration: Optional[str] = None
    audioUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    fileRef: Optional[str] = None
    mimeType: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    domain: Optional[str] = None
    fileSize: Optional[str] = None
    pages: Optional[int] = None
    favorite: Optional[bool] = False

class KnowledgeItemUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    entities: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    categoryData: Optional[Dict[str, Any]] = None
    category_fields: Optional[Dict[str, Any]] = None
    subtype: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    needs_review: Optional[bool] = False
    imageCategory: Optional[str] = None
    rawOcrText: Optional[str] = None
    suggestedReminders: Optional[List[Dict[str, Any]]] = None
    favorite: Optional[bool] = None

class KnowledgeItemResponse(BaseModel):
    id: str
    title: str
    type: str
    category: str
    createdAt: str
    summary: str
    content: str
    tags: List[str]
    entities: List[str]
    keywords: Optional[List[str]] = []
    detectedEvents: List[Dict[str, Any]]
    suggestedReminders: Optional[List[Dict[str, Any]]] = []
    categoryData: Optional[Dict[str, Any]] = None
    category_fields: Optional[Dict[str, Any]] = None
    subtype: Optional[str] = None
    confidence: Optional[float] = None
    reason: Optional[str] = None
    needs_review: Optional[bool] = False
    imageCategory: Optional[str] = None
    rawOcrText: Optional[str] = None
    ocrConfidence: Optional[float] = None
    ocrDetails: Optional[Dict[str, Any]] = None
    normalizedDates: Optional[List[Dict[str, Any]]] = []
    processingStatus: Optional[str] = "completed"
    isSensitive: Optional[bool] = False
    ownerId: Optional[str] = None
    favorite: bool
    duration: Optional[str] = None
    audioUrl: Optional[str] = None
    imageUrl: Optional[str] = None
    fileRef: Optional[str] = None
    mimeType: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    url: Optional[str] = None
    domain: Optional[str] = None
    fileSize: Optional[str] = None
    pages: Optional[int] = None

class ConfirmReminderRequest(BaseModel):
    title: str
    dueDate: str
    priority: Optional[str] = "normal"

# ==========================================
# 2. Reminder Schemas
# ==========================================
class ReminderCreate(BaseModel):
    title: str
    dueDate: str
    priority: str = "normal"
    sourceId: Optional[str] = None
    sourceTitle: Optional[str] = None

class ReminderResponse(BaseModel):
    id: str
    title: str
    dueDate: str
    priority: str
    completed: bool
    sourceId: Optional[str] = None
    sourceTitle: Optional[str] = None

# ==========================================
# 3. Conversational RAG & Chat Schemas
# ==========================================
class ChatMessage(BaseModel):
    sender: str
    text: str

class ChatQuery(BaseModel):
    prompt: str
    history: Optional[List[Dict[str, Any]]] = []

class SourceCitation(BaseModel):
    id: str
    title: str
    type: str
    summary: str
    relevance: str

class ChatResponse(BaseModel):
    reply: str
    sources: List[SourceCitation]

# ==========================================
# 4. Multi-Modal Processing Schemas
# ==========================================
class ProcessNoteRequest(BaseModel):
    text: str
    title: Optional[str] = None
    category: Optional[str] = "General"

class ProcessLinkRequest(BaseModel):
    url: str

class MultiModalProcessResponse(BaseModel):
    title: str
    summary: str
    content: str
    tags: List[str]
    entities: List[str]
    detectedEvents: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

# ==========================================
# 5. Auth & User Schemas
# ==========================================
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    name: str
    email: str
    password: str

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    privacyMode: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    avatar: str
    plan: str
    storageUsed: str
    storageLimit: str
    privacyMode: str
    token: Optional[str] = None

class MetadataUpdate(BaseModel):
    category: Optional[str] = None
    subtype: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    category_fields: Optional[Dict[str, Any]] = None
    keywords: Optional[List[str]] = None
    event_date: Optional[str] = None
    location: Optional[str] = None
    needs_review: Optional[bool] = None
    reason: Optional[str] = None


class ImageClassificationResult(BaseModel):
    category: str
    subtype: Optional[str] = None
    confidence: float
    reason: str
    title: str
    summary: str
    extracted_text: str
    keywords: List[str] = []
    extracted_entities: List[str] = []
    category_fields: Dict[str, Any] = {}
    needs_review: bool = False

