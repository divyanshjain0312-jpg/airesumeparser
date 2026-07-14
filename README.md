AI Resume Parser + Skill Gap Analyzer

A full-stack AI application with two features:


Resume Parser — Upload a PDF resume and query it using a RAG (Retrieval-Augmented Generation) pipeline.
Skill Gap & Course Finder — Paste a job description to see which skills you're missing, get YouTube course recommendations to close the gap, and receive an ATS-optimized resume rewrite.


Feature 1:  PDF → Extract → Chunk → Embed → FAISS → Retrieve → LLM → Answer
Feature 2:  Resume + Job Description → Skill Gap → YouTube Courses + ATS Rewrite


Tech Stack

LayerTechnologyFrontendNext.js 16, React 19, TypeScript, Tailwind CSSBackendFastAPI, Python 3.11PDF ParsingPyMuPDFChunkingLangChain (6 strategies)EmbeddingsSentenceTransformers (HuggingFace)Vector DatabaseFAISSLLMsGoogle Gemini / OpenAI / Anthropic Claude / Ollama (local)Course DataYouTube Data API v3


Project Structure

airesparser/
│
├── backend/
│   ├── app/
│   │   ├── chunkers/          # 6 chunking strategies
│   │   ├── embeddings/        # SentenceTransformer embedder
│   │   ├── factories/         # Dynamic component selection
│   │   ├── llms/              # Gemini, OpenAI, Claude, Ollama
│   │   ├── models/            # Pydantic schemas
│   │   ├── routers/           # API endpoints (upload, process, query, analyze-jd)
│   │   ├── services/          # RAG + skill-gap + youtube logic
│   │   ├── utils/             # PDF extractor, logger, skill extractor
│   │   ├── vectordb/          # FAISS session manager
│   │   ├── config.py          # Settings from .env
│   │   └── main.py            # FastAPI app entry point
│   ├── uploads/               # Uploaded PDFs (auto-created)
│   ├── vector_db/             # FAISS indexes (auto-created)
│   ├── .env                   # Your secrets (never commit this)
│   ├── .env.example           # Template for .env
│   └── requirements.txt       # Python dependencies
│
└── frontend/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   ├── page.tsx           # Resume Parser page
    │   └── skill-gap/
    │       └── page.tsx       # Skill Gap & Courses page
    ├── components/
    │   ├── accordion.tsx
    │   ├── sidebar.tsx        # Config sidebar
    │   ├── status-badge.tsx
    │   ├── status-card.tsx
    │   └── tabs.tsx           # Tab navigation
    ├── lib/
    │   ├── api.ts             # Typed API client
    │   └── utils.ts
    ├── .env.local             # Frontend env (API URL)
    └── package.json


Prerequisites

Install these once before anything else.

1. Python 3.11


⚠️ Must be Python 3.11. Python 3.13 has a known incompatibility with pydantic-core on Windows.



Download: https://www.python.org/downloads/release/python-31110/


Choose Windows installer (64-bit)
✅ Check "Add python.exe to PATH" during install


Verify:

cmdpy -3.11 --version

2. Node.js 18+

Download the LTS version: https://nodejs.org

Verify:

cmdnode --version

3. pnpm

cmdnpm install -g pnpm

4. API Keys

ProviderGet key fromNeeded forGoogle Geminihttps://aistudio.google.com/apikeyLLM (recommended)OpenAIhttps://platform.openai.com/api-keysLLM (optional)Anthropic Claudehttps://console.anthropic.comLLM (optional)Ollama (local)https://ollama.com/downloadFree local LLM (optional)YouTube Data APIhttps://console.cloud.google.comCourse recommendations


For beginners: use Ollama (free local LLM, no key) + a YouTube API key (free, for courses).




Setup — Backend

Step 1 — Go to the backend folder

cmdcd C:\Projects\airesparser\backend

Step 2 — Create a Python 3.11 virtual environment

cmdpy -3.11 -m venv .venv

Step 3 — Activate it

Windows (Command Prompt):

cmd.venv\Scripts\activate.bat

Windows (PowerShell):

powershell.venv\Scripts\Activate.ps1

Mac/Linux:

bashsource .venv/bin/activate

You should see (.venv) at the start of your prompt. Always activate before running backend commands.

Step 4 — Install dependencies

cmdpip install -r requirements.txt


⏳ Takes 3–10 minutes (downloads PyTorch + SentenceTransformers, ~1.5 GB). One-time step.



Step 5 — Create your environment file

Windows:

cmdcopy .env.example .env

Mac/Linux:

bashcp .env.example .env

Step 6 — Add your keys to .env

Open backend/.env and fill in what you'll use:

env# LLM (pick at least one)
GEMINI_API_KEY=AIzaSy...your-key
GEMINI_MODEL=gemini-2.0-flash

# YouTube course recommendations (optional but recommended)
YOUTUBE_API_KEY=AIza...your-youtube-key

# Ollama (if using local LLM — no key needed)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2

Step 7 — Start the backend

cmduvicorn app.main:app --reload --port 8000

✅ Success:

INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.

Verify at http://localhost:8000/docs — you should see /api/upload, /api/process, /api/query, and /api/analyze-jd.


Keep this terminal running.




Setup — Frontend

Open a second terminal (leave the backend running).

Step 1 — Go to the frontend folder

cmdcd C:\Projects\airesparser\frontend

Step 2 — Verify .env.local

It should contain:

envNEXT_PUBLIC_API_URL=http://localhost:8000

Step 3 — Install dependencies

cmdpnpm install

Step 4 — Start the frontend

cmdpnpm dev

✅ Success:

▲ Next.js 16.2.6
- Local:   http://localhost:3000

Open http://localhost:3000.


Getting a YouTube API Key

Needed for course recommendations on the Skill Gap page.


Go to https://console.cloud.google.com
Create a project (or select an existing one)
In the search bar, find "YouTube Data API v3" → click Enable
Go to APIs & Services → Credentials → Create Credentials → API key
Copy the key into backend/.env as YOUTUBE_API_KEY=...
Restart the backend



Free quota: 10,000 units/day (~100 searches). Each missing skill uses 1 cached search. Without a key, skill gaps still show — just without videos.



Using the App

Feature 1 — Resume Parser (homepage)


Upload a PDF resume — click the upload area in the sidebar, pick a PDF. Wait for the green checkmark.
Configure RAG settings (or leave defaults):
SettingDefaultPurposeChunking StrategyRecursive CharacterHow text is splitEmbedding Modelall-MiniLM-L6-v2Text → vectorsVector DatabaseFAISSStores/searches vectorsLLMGeminiGenerates answersChunk Size1000Max chars per chunkChunk Overlap200Overlap between chunksTop K5Chunks retrieved


Click "Process Resume" — first run downloads the embedding model (~90 MB, 30–60s). Later runs take 2–5s.
When done, the status cards show Complete and the accordions fill with real data.
Ask a question in the "Ask the Resume" box (e.g. "What languages does this candidate know?") and click Ask.


Feature 2 — Skill Gap & Courses


Process a resume on the homepage first (Feature 1).
Click the Skill Gap & Courses tab at the top.
Paste a full job description into the box.
Click Analyze Gap.
You'll see:

A match score ring (% of JD skills your resume covers)
Skills You Have (green chips)
Skills to Learn — each expands to show YouTube courses
An ATS-Optimized Resume rewrite (with a Copy button)
Debug logs with timings






The Skill Gap page reuses the resume and settings from the homepage. The LLM you pick in the sidebar carries over automatically.




API Endpoints

Base URL: http://localhost:8000

MethodEndpointPurposeGET/healthCheck backend is runningGET/docsSwagger UIPOST/api/uploadUpload a PDF resumePOST/api/processRun PDF→chunk→embed→FAISSPOST/api/queryAsk a question about the resumePOST/api/analyze-jdSkill gap + courses + ATS rewrite


Supported Components

Chunking Strategies

Recursive Character, Fixed Size, Token-based, Sentence-based, Semantic, Document Based

Embedding Models

NameHuggingFace modelall-MiniLM-L6-v2sentence-transformers/all-MiniLM-L6-v2BGE SmallBAAI/bge-small-en-v1.5BGE BaseBAAI/bge-base-en-v1.5E5 Smallintfloat/e5-small-v2Instructorhkunlp/instructor-base

LLM Providers

NameRequiresGeminiGEMINI_API_KEYOpenAIOPENAI_API_KEYClaudeANTHROPIC_API_KEYOllama / Llama / MistralOllama installed locally


How to Restart the Project

Terminal 1 — Backend:

cmdcd C:\Projects\airesparser\backend
.venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000

Terminal 2 — Frontend:

cmdcd C:\Projects\airesparser\frontend
pnpm dev

Then open http://localhost:3000. No need to reinstall dependencies.




Important Notes


.env changes need a manual restart — uvicorn --reload only watches .py files. Press Ctrl+C and restart after editing .env.
First Process Resume is slow — the embedding model downloads ~90 MB on first run, then it's cached.
Sessions are in-memory — restarting the backend clears them. Re-process before querying/analyzing.
Config carries between tabs — the Skill Gap page reuses the homepage's session and LLM choice. If you change the LLM after processing, re-process so the change is saved.
ATS rewrites are truthful — the prompt forbids inventing skills you don't have; it only rephrases genuine experience with better keywords.
FAISS only — the sidebar shows a Vector Database dropdown, but the backend always uses FAISS by design.



Environment Variables Reference

Full backend/.env:

env# === LLM API Keys (fill the ones you'll use) ===
GEMINI_API_KEY=your_gemini_key_here
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# === Model Names ===
GEMINI_MODEL=gemini-2.0-flash
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_MODEL=claude-3-5-haiku-latest

# === Ollama (local, no key needed) ===
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2

# === YouTube Data API (for course recommendations) ===
YOUTUBE_API_KEY=your_youtube_key_here

# === Paths (don't change unless you move folders) ===
UPLOAD_DIR=./uploads
VECTOR_DB_DIR=./vector_db

# === CORS (add your frontend URL if deploying) ===
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

Full frontend/.env.local:

envNEXT_PUBLIC_API_URL=http://localhost:8000
