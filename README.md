# AI Resume Parser — Full Stack RAG Application

A full-stack AI application that parses resumes using a **RAG (Retrieval-Augmented Generation)** pipeline.
Upload a PDF resume, configure the AI components, ask questions, and get intelligent answers powered by real embeddings and an LLM.

```
PDF Upload → Text Extraction → Chunking → Embeddings → FAISS → Retrieval → LLM → Answer
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| PDF Parsing | PyMuPDF |
| Chunking | LangChain (4 strategies) |
| Embeddings | SentenceTransformers (HuggingFace) |
| Vector Database | FAISS |
| LLMs | Google Gemini / OpenAI / Anthropic Claude / Ollama (local) |

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
│   │   ├── models/            # Pydantic request/response schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # RAG orchestration logic
│   │   ├── utils/             # PDF extractor, debug logger
│   │   ├── vectordb/          # FAISS session manager
│   │   ├── config.py          # Settings from .env
│   │   └── main.py            # FastAPI app entry point
│   ├── uploads/               # Uploaded PDFs (auto-created)
│   ├── vector_db/             # FAISS indexes (auto-created)
│   ├── .env                   # Your secrets (never commit this)
│   ├── .env.example           # Template for .env
│   ├── requirements.txt       # Python dependencies
│   └── README.md
│
└── frontend/
    ├── app/
    │   ├── globals.css
    │   ├── layout.tsx
    │   └── page.tsx           # Main page (replaced)
    ├── components/
    │   ├── accordion.tsx
    │   ├── sidebar.tsx        # Sidebar with config (replaced)
    │   ├── status-badge.tsx
    │   └── status-card.tsx
    ├── lib/
    │   ├── api.ts             # Typed API client (new)
    │   └── utils.ts
    ├── .env.local             # Frontend env (API URL)
    └── package.json
```

---

## Prerequisites

Install these once on your machine before anything else.

### 1. Python 3.11
> ⚠️ Must be Python 3.11. Python 3.13 has a known incompatibility with pydantic-core on Windows.

Download from: https://www.python.org/downloads/release/python-31110/
- Choose **Windows installer (64-bit)**
- ✅ Check **"Add python.exe to PATH"** during install

Verify:
```cmd
py -3.11 --version
```
Expected: `Python 3.11.x`

---

### 2. Node.js 18+
Download from: https://nodejs.org
- Choose the **LTS** version

Verify:
```cmd
node --version
```
Expected: `v18.x.x` or higher

---

### 3. pnpm
```cmd
npm install -g pnpm
```

Verify:
```cmd
pnpm --version
```

---

### 4. An LLM API Key (choose one)

| Provider | Get key from | Free tier |
|---|---|---|
| Google Gemini | https://aistudio.google.com/apikey | Yes (limited) |
| OpenAI | https://platform.openai.com/api-keys | Paid |
| Anthropic Claude | https://console.anthropic.com | Paid |
| Ollama (local) | https://ollama.com/download | Free, no key needed |

> **Recommendation for beginners:** Use **Ollama** — it's completely free, runs locally, no API key needed. Setup guide is below.

---

## Setup — Backend

### Step 1 — Open terminal and go to the backend folder

```cmd
cd C:\Projects\airesparser\backend
```

### Step 2 — Create a Python 3.11 virtual environment

```cmd
py -3.11 -m venv .venv
```

### Step 3 — Activate the virtual environment

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

You should see `(.venv)` at the start of your prompt. Always activate before running any backend command.

### Step 4 — Install Python dependencies

```cmd
pip install -r requirements.txt
```

> ⏳ This takes 3–10 minutes. It downloads PyTorch and SentenceTransformers which are large packages (~1.5 GB total). This is a one-time step.

### Step 5 — Create your environment file

**Windows:**
```cmd
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

### Step 6 — Add your API key to `.env`

Open `backend/.env` in any text editor (Notepad, VS Code, etc.) and fill in your key:

**If using Gemini:**
```env
GEMINI_API_KEY=AIzaSy...your-actual-key-here
GEMINI_MODEL=gemini-2.0-flash
```

**If using OpenAI:**
```env
OPENAI_API_KEY=sk-...your-actual-key-here
```

**If using Anthropic Claude:**
```env
ANTHROPIC_API_KEY=sk-ant-...your-actual-key-here
```

**If using Ollama (no key needed):**
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
```

Leave all other lines as they are.

### Step 7 — Start the backend server

```cmd
uvicorn app.main:app --reload --port 8000
```

✅ **Success looks like this:**
```
INFO:     Will watch for changes in these directories: [...]
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

Verify it works by opening: **http://localhost:8000/docs**
You should see the Swagger UI with 4 endpoints listed.

> Keep this terminal open and running. Do not close it.

---

## Setup — Frontend

Open a **second terminal** (leave the backend terminal running).

### Step 1 — Go to the frontend folder

```cmd
cd C:\Projects\airesparser\frontend
```

### Step 2 — Verify the environment file exists

Check that `.env.local` exists and contains:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If the file is missing, create it with that content.

### Step 3 — Install dependencies

```cmd
pnpm install
```

> ⏳ This takes 1–2 minutes. One-time step.

### Step 4 — Start the frontend

```cmd
pnpm dev
```

✅ **Success looks like this:**
```
▲ Next.js 16.2.6
- Local:   http://localhost:3000
- Ready in 2.1s
```

Open **http://localhost:3000** in your browser.

---

## Ollama Setup (Free, Local LLM)

Use this if you don't want to use paid API keys.

### Step 1 — Install Ollama
Download from: **https://ollama.com/download** → click **Download for Windows**

Run `OllamaSetup.exe`. It installs automatically as a background service.

### Step 2 — Open a new terminal and pull the model

```cmd
ollama pull llama3.2
```

> ⏳ Downloads ~2 GB. Wait for it to complete fully.

### Step 3 — Test it works

```cmd
ollama run llama3.2 "say hello"
```

You should get a short reply. Press `Ctrl+C` to exit.

### Step 4 — Verify backend `.env` has Ollama settings

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=llama3.2
```

### Step 5 — Use Ollama in the app

In the frontend sidebar, change the **LLM dropdown** to `Llama (via Ollama)` before clicking Ask.

> 💡 If responses are slow, use the smaller model instead:
> ```cmd
> ollama pull llama3.2:1b
> ```
> Then set `OLLAMA_DEFAULT_MODEL=llama3.2:1b` in `.env` and restart the backend.

---

## Using the Application

### Full workflow step by step:

**1. Upload a resume**
- Click the upload area in the left sidebar
- Select any PDF resume file
- Wait for the green checkmark ✅ and filename to appear

**2. Configure RAG settings** (or leave defaults)

| Setting | Default | What it does |
|---|---|---|
| Chunking Strategy | Recursive Character | How the text is split into chunks |
| Embedding Model | all-MiniLM-L6-v2 | Converts text to vectors |
| Vector Database | FAISS | Stores and searches vectors |
| LLM | Gemini | Generates the final answer |
| Chunk Size | 1000 | Max characters per chunk |
| Chunk Overlap | 200 | Overlap between chunks |
| Top K | 5 | How many chunks to retrieve |

**3. Click "Process Resume"**
- Button shows a spinner while processing
- First run downloads the embedding model (~90 MB) — takes 30–60 seconds
- Subsequent runs take 2–5 seconds
- When done, all 4 status cards show **Complete**

**4. Ask a question**
- Type in the "Ask the Resume" box
- Example questions:
  - `Summarize this candidate's experience`
  - `What programming languages does this candidate know?`
  - `What is their highest level of education?`
  - `How many years of experience do they have?`
- Click **Ask**

**5. View results**
- Scroll down to **Analysis Results**
- Open each accordion to see:
  - **Extracted Text Preview** — raw text from the PDF
  - **Chunk Preview** — how the text was split
  - **Retrieved Chunks** — the most relevant pieces for your question
  - **Final Prompt Sent to LLM** — exact prompt constructed
  - **LLM Answer** — the AI's response
  - **Source Chunks** — chunks with similarity scores
  - **Debug Logs** — full pipeline timeline with timings

---

## API Endpoints

Base URL: `http://localhost:8000`

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check if backend is running |
| GET | `/docs` | Swagger UI (interactive API docs) |
| POST | `/api/upload` | Upload a PDF resume |
| POST | `/api/process` | Run the RAG ingestion pipeline |
| POST | `/api/query` | Ask a question about the resume |

---

## Supported Components

### Chunking Strategies
| Frontend name | Strategy |
|---|---|
| Recursive Character | Splits on `\n\n`, `\n`, `.`, ` ` — best general purpose |
| Fixed Size | Exact character count chunks |
| Token-based | Splits by token count (uses tiktoken) |
| Sentence-based | Splits on sentence boundaries (uses NLTK) |
| Semantic | Groups sentences by embedding similarity |
| Document Based | Splits on paragraph/section boundaries |

### Embedding Models
| Frontend name | HuggingFace model | Notes |
|---|---|---|
| all-MiniLM-L6-v2 | sentence-transformers/all-MiniLM-L6-v2 | Best default, fast |
| BGE Small | BAAI/bge-small-en-v1.5 | Good retrieval quality |
| BGE Base | BAAI/bge-base-en-v1.5 | Better quality, slower |
| E5 Small | intfloat/e5-small-v2 | Good for Q&A tasks |
| Instructor | hkunlp/instructor-base | Instruction-tuned |

### LLM Providers
| Frontend name | Provider | Requires |
|---|---|---|
| Gemini | Google Gemini API | `GEMINI_API_KEY` in `.env` |
| OpenAI | OpenAI GPT | `OPENAI_API_KEY` in `.env` |
| Claude | Anthropic Claude | `ANTHROPIC_API_KEY` in `.env` |
| Ollama (local) | Ollama | Ollama installed locally |
| Llama (via Ollama) | Meta Llama via Ollama | Ollama + `ollama pull llama3.2` |
| Mistral (via Ollama) | Mistral via Ollama | Ollama + `ollama pull mistral` |

---

## How to Restart the Project

Every time you want to run the project again:

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

Then open **http://localhost:3000**.

> You do NOT need to reinstall dependencies again. Just activate the venv and start both servers.

---

## Troubleshooting

### Backend won't start

| Error | Fix |
|---|---|
| `DLL load failed` / pydantic error | You're using Python 3.13. Delete `.venv`, create it with `py -3.11 -m venv .venv` |
| `ModuleNotFoundError` | Virtual environment not activated. Run `.venv\Scripts\activate.bat` first |
| `Address already in use` | Port 8000 is taken. Kill the old process or use `--port 8001` |

### API Errors

| Error | Fix |
|---|---|
| `404 This model is no longer available` | Change `GEMINI_MODEL=gemini-2.0-flash` in `.env`, restart uvicorn |
| `429 Quota exceeded` | Free tier limit hit. Get a new API key, enable billing, or switch to Ollama |
| `GEMINI_API_KEY is not configured` | `.env` file missing or not loaded. Make sure `.env` exists in `backend/` folder |
| `No processed session found` | You need to click **Process Resume** before clicking **Ask** |
| `Embedding dimension mismatch` | You changed the embedding model after processing. Re-click Process Resume |

### Frontend errors

| Error | Fix |
|---|---|
| CORS error in browser console | Backend isn't running on port 8000 |
| `Cannot find module '@/lib/utils'` | Create `frontend/lib/utils.ts` — see below |
| Blank page | Check browser console (F12) for errors |

**`frontend/lib/utils.ts`** (create if missing):
```ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### Ollama errors

| Error | Fix |
|---|---|
| `connection refused` | Ollama isn't running. Launch it from Start Menu |
| `model not found` | Run `ollama pull llama3.2` in terminal |
| Very slow responses | Normal on CPU. Try `ollama pull llama3.2:1b` for a faster smaller model |

---

## Important Notes

- **`.env` changes require a manual restart** — uvicorn `--reload` only watches `.py` files, not `.env`. Always press `Ctrl+C` and restart after editing `.env`.
- **First Process Resume is slow** — the embedding model downloads ~90 MB on first run. Subsequent runs are fast because the model is cached.
- **Session is in-memory** — if you restart the backend, you need to click **Process Resume** again before asking questions.
- **One session per upload** — uploading a new PDF automatically creates a new session and clears previous results.
- **FAISS only** — even though the sidebar shows a Vector Database dropdown, the backend always uses FAISS regardless of selection (by design).

---

## Environment Variables Reference

Full list of variables for `backend/.env`:

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

# === Paths (do not change unless you move folders) ===
UPLOAD_DIR=./uploads
VECTOR_DB_DIR=./vector_db

# === CORS (add your frontend URL if deploying) ===
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```
