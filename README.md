# AI Resume Parser + Skill Gap Analyzer

A full-stack AI application with two features:

1. **Resume Parser** — Upload a PDF resume and query it using a **RAG (Retrieval-Augmented Generation)** pipeline.
2. **Skill Gap & Course Finder** — Paste a job description to see which skills you're missing, get **YouTube course recommendations** to close the gap, and receive an **ATS-optimized resume rewrite**.

```
Feature 1:  PDF → Extract → Chunk → Embed → FAISS → Retrieve → LLM → Answer
Feature 2:  Resume + Job Description → Skill Gap → YouTube Courses + ATS Rewrite
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| PDF Parsing | PyMuPDF |
| Chunking | LangChain (6 strategies) |
| Embeddings | SentenceTransformers (HuggingFace) |
| Vector Database | FAISS |
| LLMs | Google Gemini / OpenAI / Anthropic Claude / Ollama (local) |
| Course Data | YouTube Data API v3 |

---

## Project Structure

```
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
```

---

## Prerequisites

Install these once before anything else.

### 1. Python 3.11
> ⚠️ Must be Python 3.11. Python 3.13 has a known incompatibility with pydantic-core on Windows.

Download: https://www.python.org/downloads/release/python-31110/
- Choose **Windows installer (64-bit)**
- ✅ Check **"Add python.exe to PATH"** during install

Verify:
```cmd
py -3.11 --version
```

### 2. Node.js 18+
Download the **LTS** version: https://nodejs.org

Verify:
```cmd
node --version
```

### 3. pnpm
```cmd
npm install -g pnpm
```

### 4. API Keys

| Provider | Get key from | Needed for |
|---|---|---|
| Google Gemini | https://aistudio.google.com/apikey | LLM (recommended) |
| OpenAI | https://platform.openai.com/api-keys | LLM (optional) |
| Anthropic Claude | https://console.anthropic.com | LLM (optional) |
| Ollama (local) | https://ollama.com/download | Free local LLM (optional) |
| **YouTube Data API** | https://console.cloud.google.com | **Course recommendations** |

> For beginners: use **Ollama** (free local LLM, no key) + a **YouTube API key** (free, for courses).

---

## Setup — Backend

### Step 1 — Go to the backend folder
```cmd
cd C:\Projects\airesparser\backend
```

### Step 2 — Create a Python 3.11 virtual environment
```cmd
py -3.11 -m venv .venv
```

### Step 3 — Activate it

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```
**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```
**Mac/Linux:**
```bash
source .venv/bin/activate
```

You should see `(.venv)` at the start of your prompt. Always activate before running backend commands.

### Step 4 — Install dependencies
```cmd
pip install -r requirements.txt
```
> ⏳ Takes 3–10 minutes (downloads PyTorch + SentenceTransformers, ~1.5 GB). One-time step.

### Step 5 — Create your environment file

**Windows:**
```cmd
copy .env.example .env
```
**Mac/Linux:**
```bash
cp .env.example .env
```

### Step 6 — Add your keys to `.env`

Open `backend/.env` and fill in what you'll use:

```env
# LLM (pick at least one)
GEMINI_API_KEY=AIzaSy...your-key
GEMINI_MODEL=gemini-2.0-flash

# YouTube course recommendations (optional but recommended)
YOUTUBE_API_KEY=AIza...your-youtube-key

# Ollama (if using local LLM — no key needed)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
```

### Step 7 — Start the backend
```cmd
uvicorn app.main:app --reload --port 8000
```

✅ Success:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Verify at **http://localhost:8000/docs** — you should see `/api/upload`, `/api/process`, `/api/query`, and `/api/analyze-jd`.

> Keep this terminal running.

---

## Setup — Frontend

Open a **second terminal** (leave the backend running).

### Step 1 — Go to the frontend folder
```cmd
cd C:\Projects\airesparser\frontend
```

### Step 2 — Verify `.env.local`
It should contain:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 3 — Install dependencies
```cmd
pnpm install
```

### Step 4 — Start the frontend
```cmd
pnpm dev
```

✅ Success:
```
▲ Next.js 16.2.6
- Local:   http://localhost:3000
```

Open **http://localhost:3000**.

---

## Getting a YouTube API Key

Needed for course recommendations on the Skill Gap page.

1. Go to https://console.cloud.google.com
2. Create a project (or select an existing one)
3. In the search bar, find **"YouTube Data API v3"** → click **Enable**
4. Go to **APIs & Services → Credentials → Create Credentials → API key**
5. Copy the key into `backend/.env` as `YOUTUBE_API_KEY=...`
6. Restart the backend

> Free quota: 10,000 units/day (~100 searches). Each missing skill uses 1 cached search. Without a key, skill gaps still show — just without videos.

---

## Ollama Setup (Free Local LLM)

Use this to avoid paid API keys.

### Step 1 — Install
Download: https://ollama.com/download → run `OllamaSetup.exe`. It runs as a background service.

### Step 2 — Pull a model
```cmd
ollama pull llama3.2
```
> ⏳ Downloads ~2 GB.

### Step 3 — Test
```cmd
ollama run llama3.2 "say hello"
```

### Step 4 — Use it
In the sidebar LLM dropdown, choose **Llama (via Ollama)** before processing/asking.

> 💡 For faster responses use the smaller model: `ollama pull llama3.2:1b`, then set `OLLAMA_DEFAULT_MODEL=llama3.2:1b` in `.env`.

> ⚠️ Ollama is slower than Gemini. The Skill Gap feature makes 3–4 LLM calls, so it's noticeably slower on Ollama. If you get "No JSON found" errors, the model is too small — switch to Gemini for that feature.

---

## Using the App

### Feature 1 — Resume Parser (homepage)

1. **Upload a PDF resume** — click the upload area in the sidebar, pick a PDF. Wait for the green checkmark.
2. **Configure RAG settings** (or leave defaults):

   | Setting | Default | Purpose |
   |---|---|---|
   | Chunking Strategy | Recursive Character | How text is split |
   | Embedding Model | all-MiniLM-L6-v2 | Text → vectors |
   | Vector Database | FAISS | Stores/searches vectors |
   | LLM | Gemini | Generates answers |
   | Chunk Size | 1000 | Max chars per chunk |
   | Chunk Overlap | 200 | Overlap between chunks |
   | Top K | 5 | Chunks retrieved |

3. **Click "Process Resume"** — first run downloads the embedding model (~90 MB, 30–60s). Later runs take 2–5s.
4. When done, the status cards show **Complete** and the accordions fill with real data.
5. **Ask a question** in the "Ask the Resume" box (e.g. "What languages does this candidate know?") and click **Ask**.

### Feature 2 — Skill Gap & Courses

1. Process a resume on the homepage first (Feature 1).
2. Click the **Skill Gap & Courses** tab at the top.
3. Paste a full job description into the box.
4. Click **Analyze Gap**.
5. You'll see:
   - A **match score** ring (% of JD skills your resume covers)
   - **Skills You Have** (green chips)
   - **Skills to Learn** — each expands to show YouTube courses
   - An **ATS-Optimized Resume** rewrite (with a Copy button)
   - Debug logs with timings

> The Skill Gap page reuses the resume and settings from the homepage. The LLM you pick in the sidebar carries over automatically.

---

## API Endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check backend is running |
| GET | `/docs` | Swagger UI |
| POST | `/api/upload` | Upload a PDF resume |
| POST | `/api/process` | Run PDF→chunk→embed→FAISS |
| POST | `/api/query` | Ask a question about the resume |
| POST | `/api/analyze-jd` | Skill gap + courses + ATS rewrite |

---

## Supported Components

### Chunking Strategies
Recursive Character, Fixed Size, Token-based, Sentence-based, Semantic, Document Based

### Embedding Models
| Name | HuggingFace model |
|---|---|
| all-MiniLM-L6-v2 | sentence-transformers/all-MiniLM-L6-v2 |
| BGE Small | BAAI/bge-small-en-v1.5 |
| BGE Base | BAAI/bge-base-en-v1.5 |
| E5 Small | intfloat/e5-small-v2 |
| Instructor | hkunlp/instructor-base |

### LLM Providers
| Name | Requires |
|---|---|
| Gemini | `GEMINI_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |
| Claude | `ANTHROPIC_API_KEY` |
| Ollama / Llama / Mistral | Ollama installed locally |

---

## How to Restart the Project

**Terminal 1 — Backend:**
```cmd
cd C:\Projects\airesparser\backend
.venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```cmd
cd C:\Projects\airesparser\frontend
pnpm dev
```

Then open **http://localhost:3000**. No need to reinstall dependencies.

---

## Troubleshooting

### Backend
| Error | Fix |
|---|---|
| `DLL load failed` / pydantic error | Using Python 3.13. Delete `.venv`, recreate with `py -3.11 -m venv .venv` |
| `ModuleNotFoundError` | Virtual environment not activated. Run `.venv\Scripts\activate.bat` |
| `Address already in use` | Port 8000 taken. Use `--port 8001` |

### API / LLM
| Error | Fix |
|---|---|
| `404 model no longer available` | Set `GEMINI_MODEL=gemini-2.0-flash` in `.env`, **restart uvicorn** |
| `429 Quota exceeded` | Free tier limit hit. New API key, enable billing, or switch to Ollama |
| `GEMINI_API_KEY is not configured` | `.env` missing or not loaded. Ensure `.env` exists in `backend/`, restart |
| `No processed session found` | Click **Process Resume** before asking questions or analyzing a JD |
| Skill Gap uses wrong LLM | The saved config is stale. Re-select the LLM on the homepage, then re-process (or apply the config-sync fix) |

### Skill Gap / YouTube
| Error | Fix |
|---|---|
| Skill gaps show but no videos | `YOUTUBE_API_KEY` not set, or daily quota hit |
| `YouTube API error (403)` | Quota exceeded (100 searches/day) or restricted key. Wait 24h or make a new key |
| `Analysis failed: No JSON found` | LLM didn't return clean JSON. Use Gemini/OpenAI instead of a tiny Ollama model |
| Analysis is slow | Normal — it makes 3–4 LLM calls. Ollama is slowest |

### Frontend
| Error | Fix |
|---|---|
| `Export X doesn't exist in target module` (lucide-react) | An icon name doesn't exist in your lucide version. Run the icon-check command below |
| CORS error in console | Backend not running on port 8000 |
| `Cannot find module '@/lib/utils'` | Create `frontend/lib/utils.ts` (see below) |

**Check available lucide icons:**
```cmd
node -e "console.log(Object.keys(require('lucide-react')).filter(n => /video|play|monitor/i.test(n)))"
```

**`frontend/lib/utils.ts`** (create if missing):
```ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

---

## Important Notes

- **`.env` changes need a manual restart** — uvicorn `--reload` only watches `.py` files. Press `Ctrl+C` and restart after editing `.env`.
- **First Process Resume is slow** — the embedding model downloads ~90 MB on first run, then it's cached.
- **Sessions are in-memory** — restarting the backend clears them. Re-process before querying/analyzing.
- **Config carries between tabs** — the Skill Gap page reuses the homepage's session and LLM choice. If you change the LLM after processing, re-process so the change is saved.
- **ATS rewrites are truthful** — the prompt forbids inventing skills you don't have; it only rephrases genuine experience with better keywords.
- **FAISS only** — the sidebar shows a Vector Database dropdown, but the backend always uses FAISS by design.

---

## Environment Variables Reference

Full `backend/.env`:

```env
# === LLM API Keys (fill the ones you'll use) ===
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
```

Full `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```
