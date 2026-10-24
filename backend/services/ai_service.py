import re
import urllib.request
import urllib.parse
from html.parser import HTMLParser
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple

# Pre-defined known entity dictionaries for instant extraction
KNOWN_TECH_ENTITIES = {
    "rag", "vectordb", "fastapi", "python", "docker", "qdrant", "postgresql",
    "pwa", "service worker", "indexeddb", "redis", "bge-reranker", "whisper",
    "vit", "vision ai", "multimodal", "bm25", "hybrid search", "cross-attention",
    "api gateway", "nginx", "react", "vite", "tailwind", "rest", "asyncio",
    "sqlite", "llm", "embeddings", "jwt", "oauth"
}

def extract_entities(text: str) -> List[str]:
    """Extract named technical entities and capitalized concept phrases."""
    found = set()
    lower_text = text.lower()
    
    # Check known entities
    for ent in KNOWN_TECH_ENTITIES:
        if ent in lower_text:
            # Capitalize nicely
            found.add(ent.title() if len(ent) > 4 else ent.upper())

    # Regex for capitalized multi-word phrases (e.g. "Hybrid Search", "Redis Cache")
    capitalized_phrases = re.findall(r'\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)+\b', text)
    for phrase in capitalized_phrases:
        if len(phrase.split()) <= 4 and phrase.lower() not in {"the united", "this is"}:
            found.add(phrase)

    return list(found)[:6]
 
COMMON_STOPWORDS = {
    "the", "and", "a", "an", "of", "to", "in", "is", "for", "on", "with", "as", "by", "at", "from",
    "this", "that", "it", "or", "be", "are", "from", "was", "were", "has", "have", "had", "will",
    "not", "but", "what", "which", "when", "where", "who", "whom", "how", "all", "each", "every",
    "both", "such", "can", "could", "should", "would", "than", "into", "onto", "under", "over",
    "image", "visual", "screen", "screenshot", "extracted", "confidence", "analyzed"
}

def extract_semantic_keywords(text: str) -> List[str]:
    """
    Extract key semantic terms, entities, technical abbreviations, and concepts
    optimized for RAG vector search, keyword indexing, and retrieval.
    """
    keywords = []
    seen = set()

    def add_keyword(kw: str):
        clean = kw.strip().strip(",.:;\"'()[]{}")
        if clean and len(clean) >= 2 and clean.lower() not in COMMON_STOPWORDS and clean.lower() not in seen:
            seen.add(clean.lower())
            keywords.append(clean)

    # 1. Existing named technical entities
    for ent in extract_entities(text):
        add_keyword(ent)

    # 2. Extract technical acronyms (2-6 capital alphanumeric letters, e.g. OCR, RAG, API, HTTP, SQL, CPU, GPU)
    acronyms = re.findall(r'\b[A-Z0-9]{2,6}\b', text)
    for acr in acronyms:
        if acr.lower() not in {"an", "at", "by", "do", "go", "if", "in", "is", "it", "me", "my", "no", "of", "on", "or", "so", "to", "up", "us", "we"}:
            add_keyword(acr)

    # 3. Capitalized technical terms and domain words (e.g. Architecture, Pipeline, Service, Gateway)
    words = re.findall(r'\b[A-Z][a-zA-Z0-9_-]{2,}\b', text)
    for w in words:
        add_keyword(w)

    # 4. Extract compound terms (e.g. micro-services, full-text, real-time)
    compounds = re.findall(r'\b[a-zA-Z0-9]+[-_][a-zA-Z0-9]+\b', text)
    for c in compounds:
        add_keyword(c)

    return keywords[:10]


def extract_tags(text: str, category: str = "General") -> List[str]:
    """Generate meaningful tags based on text content and keywords."""
    tags = set()
    if category and category != "General":
        tags.add(category)

    # Check for markdown hashtags
    raw_tags = re.findall(r'#(\w+)', text)
    for t in raw_tags:
        tags.add(t)

    # Common domain keyword mapping
    lower = text.lower()
    if any(k in lower for k in ["rag", "retrieval", "vector", "embedding"]):
        tags.add("RAG")
        tags.add("AI")
    if any(k in lower for k in ["fastapi", "api", "backend", "endpoint"]):
        tags.add("FastAPI")
    if any(k in lower for k in ["audio", "voice", "speech", "transcription", "whisper"]):
        tags.add("VoiceMemo")
    if any(k in lower for k in ["image", "ocr", "diagram", "vision"]):
        tags.add("OCR")
    if any(k in lower for k in ["database", "postgres", "sql", "qdrant", "redis"]):
        tags.add("Database")
    if any(k in lower for k in ["offline", "pwa", "sync", "service worker"]):
        tags.add("PWA")
        tags.add("Mobile")
    if any(k in lower for k in ["docker", "cluster", "deploy", "nginx"]):
        tags.add("DevOps")

    if not tags:
        tags.add("Captured")

    return list(tags)[:5]

def detect_deadlines_and_events(text: str, source_title: str) -> List[Dict[str, Any]]:
    """Detect actionable dates, meetings, and deadlines mentioned in text."""
    events = []
    now = datetime.utcnow()
    lower = text.lower()

    # Pattern 1: Explicit words like "tomorrow", "due tomorrow"
    if "tomorrow" in lower:
        due = now + timedelta(days=1)
        events.append({
            "id": f"ev-{int(now.timestamp() * 1000)}",
            "title": f"Follow up on: {source_title}",
            "dueDate": due.replace(hour=17, minute=0, second=0).isoformat(),
            "priority": "urgent",
            "completed": False
        })

    # Pattern 2: "due in X days"
    match_days = re.search(r'due in (\d+) days?', lower)
    if match_days:
        days = int(match_days.group(1))
        due = now + timedelta(days=days)
        events.append({
            "id": f"ev-{int(now.timestamp() * 1000) + 1}",
            "title": f"Deadline for: {source_title}",
            "dueDate": due.isoformat(),
            "priority": "urgent" if days <= 2 else "upcoming",
            "completed": False
        })

    # Pattern 3: General trigger words: "deadline", "review", "due date", "meeting"
    if not events and any(trigger in lower for trigger in ["deadline", "due date", "review benchmark", "meeting scheduled", "deliverable"]):
        due = now + timedelta(days=3)
        events.append({
            "id": f"ev-{int(now.timestamp() * 1000)}",
            "title": f"Action Item: {source_title}",
            "dueDate": due.isoformat(),
            "priority": "urgent" if "urgent" in lower or "asap" in lower else "upcoming",
            "completed": False
        })

    return events

def generate_summary(text: str, max_chars: int = 180) -> str:
    """Generate a clean executive summary of text content."""
    clean = re.sub(r'[#*`>-]', '', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', clean)
    summary = ""
    for s in sentences:
        if len(summary) + len(s) < max_chars:
            summary += (" " if summary else "") + s
        else:
            break
    if not summary:
        summary = clean[:max_chars].strip() + ("..." if len(clean) > max_chars else "")
    return summary

class _TitleAndMetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title = ""
        self.meta_desc = ""

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.in_title = True
        elif tag == "meta":
            attrs_dict = dict(attrs)
            if attrs_dict.get("name", "").lower() == "description":
                self.meta_desc = attrs_dict.get("content", "")
            elif attrs_dict.get("property", "").lower() == "og:description":
                if not self.meta_desc:
                    self.meta_desc = attrs_dict.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data

def scrape_link_metadata(url: str) -> Dict[str, Any]:
    """Fetch title, domain, and description for a web URL."""
    try:
        parsed = urllib.parse.urlparse(url if url.startswith("http") else f"https://{url}")
        domain = parsed.hostname or "web-source.com"
        
        req = urllib.request.Request(
            parsed.geturl(),
            headers={"User-Agent": "MindSync-Knowledge-Bot/1.0 (+http://localhost:5173)"}
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            content = resp.read(16384).decode("utf-8", errors="ignore")
            parser = _TitleAndMetaParser()
            parser.feed(content)
            title = parser.title.strip() or f"Article from {domain}"
            desc = parser.meta_desc.strip() or f"Curated technical web resource from {domain}"
            return {
                "title": title,
                "domain": domain,
                "summary": desc,
                "url": parsed.geturl()
            }
    except Exception:
        domain = urllib.parse.urlparse(url if url.startswith("http") else f"https://{url}").hostname or "web-source.com"
        return {
            "title": f"Bookmark: {domain}",
            "domain": domain,
            "summary": f"Web reference extracted from {domain} with full reader snapshot.",
            "url": url
        }
