export const INITIAL_KNOWLEDGE_ITEMS = [
  {
    id: "item-1",
    title: "Distributed RAG System Architecture Guidelines",
    type: "note",
    category: "Architecture",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3).toISOString(), // 3 hours ago
    summary: "Detailed structural recommendations for building a sub-100ms retrieval pipeline with hybrid vector + lexical search and re-ranking models.",
    content: `# Distributed RAG System Architecture Guidelines

### Core Principles
1. **Hybrid Retrieval**: Combine dense semantic embeddings (Cohere / OpenAI) with sparse BM25 indexing for domain-specific acronym precision.
2. **Context Compression**: Run cross-encoder reranking (e.g., bge-reranker-large) before passing top-5 chunks into the prompt context window to eliminate hallucination.
3. **Chunking Strategy**: Semantic boundary chunking at 450 tokens with 50-token overlapping sliding window.

### Cache Strategy
Store high-frequency prompt hashes in Redis with a 4-hour TTL to bypass LLM generation costs for common query patterns.`,
    tags: ["RAG", "VectorDB", "FastAPI", "AI"],
    entities: ["Hybrid Search", "BM25", "Redis Cache", "bge-reranker"],
    detectedEvents: [
      {
        id: "ev-1",
        title: "Review vector indexing latency benchmarks",
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(), // 2 days from now
        priority: "urgent",
        completed: false
      }
    ],
    favorite: true
  },
  {
    id: "item-2",
    title: "Client Product Discovery Memo - Mobile Offline First",
    type: "voice",
    category: "Product",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 18).toISOString(), // 18 hours ago
    summary: "Audio recording detailing field feedback regarding service worker offline capability, background sync, and instant voice-to-text notes.",
    duration: "03:42",
    audioUrl: null, // Simulated audio wave stream
    content: "Transcription: 'The users specifically highlighted that during transit or low-connectivity zones, they need notes and voice memos to cache immediately onto local storage, then sync with the FastAPI backend once network is re-established. Let's make sure the PWA manifest and service worker handle this seamlessly.'",
    tags: ["Mobile", "PWA", "OfflineSync", "VoiceMemo"],
    entities: ["Service Worker", "IndexedDB", "FastAPI Sync", "Background Sync"],
    detectedEvents: [
      {
        id: "ev-2",
        title: "PWA offline background sync review meeting",
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 4).toISOString(), // 4 days from now
        priority: "upcoming",
        completed: false
      }
    ],
    favorite: false
  },
  {
    id: "item-3",
    title: "Cloud Infrastructure & Microservices Topology",
    type: "image",
    category: "DevOps",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(), // 1.5 days ago
    summary: "Visual whiteboarding session diagram outlining Dockerized FastAPI services, Qdrant vector database, and PostgreSQL metadata stores.",
    imageUrl: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
    content: "Extracted OCR text: [API Gateway / Nginx Reverse Proxy] -> [FastAPI Application Cluster :8000] -> [Qdrant Vector Engine :6333] + [PostgreSQL Metadata :5432]. Backup snapshot scheduled daily at 02:00 UTC.",
    tags: ["Docker", "Qdrant", "PostgreSQL", "DevOps"],
    entities: ["Nginx", "FastAPI Cluster", "Qdrant Engine", "PostgreSQL"],
    detectedEvents: [
      {
        id: "ev-3",
        title: "Deploy Qdrant cluster migration script",
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(), // 12 hours from now
        priority: "urgent",
        completed: false
      }
    ],
    favorite: true
  },
  {
    id: "item-4",
    title: "Deep Dive into Multi-Modal Reasoning 2026.pdf",
    type: "document",
    category: "Research",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(), // 3 days ago
    fileSize: "4.8 MB",
    pages: 28,
    summary: "Academic preprint discussing unified encoders for cross-modal indexing between speech phonemes, image embeddings, and technical literature.",
    content: "Document Abstract: Recent advancements in multimodal LLMs demonstrate that cross-attention projection layers allow direct semantic alignment between Whisper acoustic tokens and ViT vision patches without intermediate transcription losses.",
    tags: ["Multimodal", "Vision", "AudioTokens", "Whitepaper"],
    entities: ["Whisper", "ViT", "Cross-Attention", "Phoneme Alignment"],
    detectedEvents: [],
    favorite: false
  },
  {
    id: "item-5",
    title: "FastAPI Documentation - High Performance Async APIs",
    type: "link",
    category: "Engineering",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 96).toISOString(), // 4 days ago
    url: "https://fastapi.tiangolo.com/tutorial/bigger-applications/",
    domain: "fastapi.tiangolo.com",
    summary: "Best practices for modular multi-file project layouts with APIRouter, dependency injection, and Pydantic v2 schemas.",
    content: "FastAPI provides native asynchronous endpoints using Python 3.10+ async/await syntax, automatic OpenAPI interactive documentation, and Pydantic v2 validation achieving performance on par with NodeJS and Go.",
    tags: ["FastAPI", "Python", "APIRouter", "Pydantic"],
    entities: ["APIRouter", "Pydantic v2", "OpenAPI", "Starlette"],
    detectedEvents: [
      {
        id: "ev-4",
        title: "Refactor backend APIRouter endpoints",
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString(), // 7 days from now
        priority: "upcoming",
        completed: false
      }
    ],
    favorite: false
  },
  {
    id: "item-6",
    title: "Q3 AI Product Strategy & Vision.pptx",
    type: "ppt",
    category: "Product",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 110).toISOString(),
    fileSize: "7.4 MB",
    pages: 22,
    summary: "Executive slide deck presenting multi-modal knowledge graph milestones, Whisper audio indexing, and automated deadline detection.",
    content: "Slide Deck Summary: 22 slides covering H2 roadmap. Key milestones include offline-first PWA sync, cross-modal semantic search, and enterprise privacy compliance.",
    tags: ["ProductRoadmap", "Slides", "PPT", "Strategy"],
    entities: ["H2 Roadmap", "Executive Deck", "Enterprise Compliance"],
    detectedEvents: [
      {
        id: "ev-5",
        title: "Present Q3 slide deck to stakeholders",
        dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 5).toISOString(),
        priority: "urgent",
        completed: false
      }
    ],
    favorite: true
  },
  {
    id: "item-7",
    title: "MindSync System Requirements Specification.docx",
    type: "docx",
    category: "Engineering",
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 130).toISOString(),
    fileSize: "1.8 MB",
    pages: 14,
    summary: "Technical requirements specification document detailing API schemas, authentication tokens, and local encrypted cache protocols.",
    content: "Document Outline: 1. Introduction 2. High-Level Architecture 3. FastAPI Service Contracts 4. Vector Embedding Storage 5. Offline Caching Strategies.",
    tags: ["Requirements", "DOCX", "Specification", "Engineering"],
    entities: ["FastAPI Contracts", "Vector Storage", "Service Contracts"],
    detectedEvents: [],
    favorite: false
  }
];

export const INITIAL_REMINDERS = [
  {
    id: "ev-3",
    title: "Deploy Qdrant cluster migration script",
    sourceId: "item-3",
    sourceTitle: "Cloud Infrastructure & Microservices Topology",
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(),
    priority: "urgent",
    completed: false
  },
  {
    id: "ev-1",
    title: "Review vector indexing latency benchmarks",
    sourceId: "item-1",
    sourceTitle: "Distributed RAG System Architecture Guidelines",
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(),
    priority: "urgent",
    completed: false
  },
  {
    id: "ev-2",
    title: "PWA offline background sync review meeting",
    sourceId: "item-2",
    sourceTitle: "Client Product Discovery Memo - Mobile Offline First",
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 4).toISOString(),
    priority: "upcoming",
    completed: false
  },
  {
    id: "ev-4",
    title: "Refactor backend APIRouter endpoints",
    sourceId: "item-5",
    sourceTitle: "FastAPI Documentation - High Performance Async APIs",
    dueDate: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7).toISOString(),
    priority: "upcoming",
    completed: false
  }
];

export const MOCK_CHAT_SUGGESTIONS = [
  "When is my next upcoming event or deadline?",
  "What are our RAG architecture guidelines?",
  "Summarize the client voice memo regarding offline support",
  "What technologies did we whiteboard for our cloud topology?",
  "Show me my research documents on multi-modal reasoning"
];
