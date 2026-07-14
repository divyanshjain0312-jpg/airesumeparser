# AI Resume Parser — Backend

FastAPI backend implementing a modular RAG pipeline:
**PDF → Clean → Chunk → Embed → FAISS → Retrieve → LLM**.

## Quick Start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # fill in at least GEMINI_API_KEY
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## Endpoints

| Method | Path         | Purpose                                                    |
| ------ | ------------ | ---------------------------------------------------------- |
| GET    | `/health`    | Liveness check                                             |
| POST   | `/api/upload`  | Upload PDF (multipart). Returns `session_id`             |
| POST   | `/api/process` | Run PDF→chunk→embed→FAISS for a session's PDF            |
| POST   | `/api/query`   | Retrieve top-K chunks + call LLM for the given question |

## Supported Options

**Chunking:** `recursive-character`, `fixed-size`, `token-based`, `sentence-based`, `semantic`, `document-based`

**Embedding models:** `all-MiniLM-L6-v2`, `bge-small`, `bge-base`, `e5-small`, `instructor`

**LLMs:** `gemini`, `openai`, `claude`, `ollama`, `llama` (Ollama), `mistral` (Ollama)

**Vector DB:** FAISS only (frontend `chromadb` value is accepted but silently uses FAISS — an explicit design choice per the task spec).

## Adding a new component

- **New chunker** → subclass `BaseChunker` in `app/chunkers/`, register in `ChunkerFactory._registry`.
- **New embedding model** → add entry to `EmbeddingFactory._registry` (HF id + optional prefixes).
- **New LLM** → subclass `BaseLLM` in `app/llms/`, add a branch in `LLMFactory.create`.

Nothing else changes.
