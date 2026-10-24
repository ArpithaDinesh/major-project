# MindSync ΓÇö AI-Powered Personal Knowledge Management PWA

MindSync is a Progressive Web App (PWA) personal knowledge management system designed for capturing, organizing, and retrieving multi-modal knowledge (text notes, voice recordings, whiteboard diagrams/images, PDF documents, and web links), and querying it using natural language (RAG-based conversational AI with source citations).

---

## ≡ƒÜÇ Key Features & Core Pages

### 1. Multi-Modal Capture Engine (`/capture` modal & FAB)
- **Text Notes**: Markdown & plain-text editor with automatic tag and category parsing.
- **Voice Memos**: In-browser audio recording with animated soundwave visualizer, timer, and simulated Whisper AI transcription.
- **Image & Diagrams**: Drag-and-drop file upload + mobile camera capture (`capture="environment"`), image preview, and OCR vision text extraction.
- **PDF & Documents**: File dropzone for PDFs, whitepapers, and documents with automatic chunking and executive summary generation.
- **Web Links**: URL bookmarking with automated metadata extraction (domain badge, title, reader mode excerpt).
- **AI Processing Stepper**: Multi-step animated ingestion pipeline (`Analyzing syntax` ΓåÆ `Extracting entities` ΓåÆ `Generating vector embeddings` ΓåÆ `Detecting calendar deadlines`).

### 2. Dashboard & Home (`/`)
- Metrics overview: Total items, voice memos, documents, pending deadlines.
- Quick ingestion shortcuts for each of the 5 input modalities.
- Recent captured items feed with content previews and category badges.
- Upcoming AI-detected events widget with priority flags.
- Floating Action Button (FAB) with electric glow for instant capture from anywhere.

### 3. Knowledge Base / Library View (`/library`)
- Grid view and compact list view toggle.
- Real-time global search across titles, summaries, tags, and full text content.
- Filter pills by content modality (Notes, Audio, Images, PDFs, Web Links).
- Category/topic filter pills (Architecture, Research, Product, Engineering, DevOps, Personal, Ideas).
- Sorting by Newest, Oldest, or Alphabetical title.

### 4. Interactive Item Detail View (`DetailModal`)
- Modal display of original content:
  - Custom dark audio player for voice memos with scrubber and transcript.
  - High-res image display with OCR extraction.
  - Document viewerpane with page count and file size.
  - Web link reader view with external link button.
  - Formatted text note reader.
- AI Executive Summary with glowing accent border.
- Extracted entity pills (technologies, organizations, concepts).
- Detected deadlines with direct links to the source content.
- Quick actions: Copy content, favorite toggle, and delete.

### 5. AI Chat / Ask Your Data (`/chat`)
- Conversational RAG interface with natural language queries.
- User messages formatted in electric indigo bubbles; assistant messages in dark surface cards.
- Suggested inquiry chips (e.g., *"When is my next upcoming event?", "What are our RAG architecture guidelines?"*).
- **Clickable Source Citation Cards**: AI answers link directly to the source items that answered the question.

### 6. AI Detected Deadlines & Events (`/reminders`)
- Chronological commitments and action items automatically identified by AI from notes and memos.
- Filter by Active, Urgent, or Completed.
- Checkbox toggle with visual strikethrough.
- Manual reminder addition modal.
- Source note clickable backlink.

### 7. Settings & Profile (`/settings`)
- User profile configuration and storage quota meter.
- **FastAPI Backend Endpoint switcher**: Live connection tester with `/health` status check.
- **Local-First Privacy Mode**: Toggle between local device storage and cloud-augmented storage.
- PWA install manager & Service worker offline cache purger.
- JSON data export and demo data reset.

### 8. Authentication Screen (`/login`)
- Clean centered dark card with radial ambient glow.
- Sign In and Create Account tabs.
- **Instant Demo Access** button for immediate evaluation with preloaded multi-modal data.

---

## ≡ƒÄ¿ Design Direction & Palette

- **Background**: Deep charcoal / near-black (`#0B0C10`).
- **Surface & Cards**: Rich dark card surface (`#13141B`, `#1A1B24`) with subtle 1px borders (`#262837`).
- **Primary Accent**: Electric Indigo / Violet (`#6366F1` / `#8B5CF6`) with soft glowing hover effects (`shadow-glow-sm`, `shadow-glow-md`).
- **Secondary Accents**: Cyan/Teal (`#06B6D4`) and Emerald (`#10B981`).
- **Typography**: Inter sans-serif with high WCAG readability contrast.
- **Responsive Layout**: Persistent sidebar on desktop; sleek bottom tab bar on mobile.

---

## ≡ƒô▒ Progressive Web App (PWA) Features

- **Web App Manifest (`public/manifest.json`)**: Configured with `standalone` display mode, `#0B0C10` theme color, and custom geometric SVG neural vault icons (192x192, 512x512).
- **Service Worker (`public/sw.js`)**: Pre-caches the application shell and static assets with Stale-While-Revalidate and offline fallback strategies.
- **Add-to-Home-Screen Hook (`usePWAInstall.js`)**: Captures `beforeinstallprompt` and renders install buttons in the header, dashboard banner, and settings page.

---

## ≡ƒ¢á Project Structure

```
Major project/
Γö£ΓöÇΓöÇ index.html                   # HTML entry point with PWA meta headers & Inter font
Γö£ΓöÇΓöÇ package.json                 # React, Vite, Tailwind CSS, Lucide icons, Router, Axios
Γö£ΓöÇΓöÇ tailwind.config.js           # Dark theme color palette, glows, animations
Γö£ΓöÇΓöÇ vite.config.js               # Vite config with FastAPI proxy
Γö£ΓöÇΓöÇ public/
Γöé   Γö£ΓöÇΓöÇ favicon.svg              # App emblem
Γöé   Γö£ΓöÇΓöÇ icon-192.svg             # PWA 192px icon
Γöé   Γö£ΓöÇΓöÇ icon-512.svg             # PWA 512px icon
Γöé   Γö£ΓöÇΓöÇ manifest.json            # Web App Manifest
Γöé   ΓööΓöÇΓöÇ sw.js                    # Service Worker caching script
Γö£ΓöÇΓöÇ backend_example/
Γöé   Γö£ΓöÇΓöÇ main.py                  # Ready-to-run FastAPI REST + RAG server
Γöé   ΓööΓöÇΓöÇ requirements.txt         # FastAPI & Uvicorn dependencies
ΓööΓöÇΓöÇ src/
    Γö£ΓöÇΓöÇ main.jsx                 # Application root & Service Worker registration
    Γö£ΓöÇΓöÇ App.jsx                  # Main routing & layout structure
    Γö£ΓöÇΓöÇ index.css                # Tailwind directives & dark custom scrollbars
    Γö£ΓöÇΓöÇ context/
    Γöé   Γö£ΓöÇΓöÇ AuthContext.jsx      # Authentication & user profile state
    Γöé   Γö£ΓöÇΓöÇ KnowledgeContext.jsx # Knowledge items, search, filters, and reminders
    Γöé   ΓööΓöÇΓöÇ ToastContext.jsx     # Floating notification popups
    Γö£ΓöÇΓöÇ hooks/
    Γöé   Γö£ΓöÇΓöÇ usePWAInstall.js     # PWA prompt detection and trigger
    Γöé   ΓööΓöÇΓöÇ useAudioRecorder.js  # Audio recorder with waveform and timer
    Γö£ΓöÇΓöÇ services/
    Γöé   Γö£ΓöÇΓöÇ api.js               # Axios client with fallback to offline local store
    Γöé   ΓööΓöÇΓöÇ mockData.js          # Realistic preloaded multi-modal knowledge items
    Γö£ΓöÇΓöÇ components/
    Γöé   Γö£ΓöÇΓöÇ common/              # Sidebar, MobileNav, Header, Toast, InstallPrompt
    Γöé   Γö£ΓöÇΓöÇ capture/             # CaptureModal, AudioWaveform
    Γöé   Γö£ΓöÇΓöÇ library/             # ContentCard, FilterBar, DetailModal
    Γöé   Γö£ΓöÇΓöÇ chat/                # ChatBubble, SourceCard
    Γöé   ΓööΓöÇΓöÇ reminders/           # ReminderItem, AddReminderModal
    ΓööΓöÇΓöÇ pages/
        Γö£ΓöÇΓöÇ AuthPage.jsx         # Sign in / Sign up / Demo access
        Γö£ΓöÇΓöÇ DashboardPage.jsx    # Metrics, recent items, reminders widget, FAB
        Γö£ΓöÇΓöÇ LibraryPage.jsx      # Grid/list knowledge base with filters
        Γö£ΓöÇΓöÇ ChatPage.jsx         # Natural language RAG conversational interface
        Γö£ΓöÇΓöÇ RemindersPage.jsx    # Extracted action items & deadlines
        ΓööΓöÇΓöÇ SettingsPage.jsx     # Profile, backend endpoint, privacy & PWA status
```

---

## ≡ƒÅâ Getting Started

### 1. Run the Frontend (Vite)

In your terminal:
```bash
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

> **Zero Setup Required**: MindSync operates with an intelligent local fallback service preloaded with realistic multi-modal data. You can test all 8 screens, create notes, record audio, upload images, filter items, and query RAG chat immediately without starting any backend.

### 2. Run the Python FastAPI Backend

To start the high-performance Python FastAPI backend:

**Option A (One-Click Launcher)**:
Double-click `start_backend.bat` or run:
```cmd
start_backend.bat
```

**Option B (Command Line)**:
```bash
pip install -r backend/requirements.txt
python backend/run.py
```

The FastAPI backend runs on **`http://localhost:8000`**:
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative Docs (ReDoc)**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Database**: Thread-safe SQLite persistence in `backend/mindsync.db` with auto-seeding.
- **RAG Engine**: Hybrid retrieval pipeline with token scoring, contextual answer synthesis, and clickable source citations.

