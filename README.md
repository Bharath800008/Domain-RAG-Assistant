# Domain RAG Assistant

A real-time, domain-specific Retrieval-Augmented Generation (RAG) web app: a FastAPI
backend with hybrid (dense + BM25) retrieval over your own documents, streamed
token-by-token to a React frontend over WebSockets.

Sample domain: **HR policy** (PTO, remote work, code of conduct — seeded automatically).

---

## Project layout

```
rag-app/
├── backend/     FastAPI app, RAG pipeline, SQLite DB, JWT auth
└── frontend/    React (Vite) app: chat, documents, explorer, analytics, settings
```
## How retrieval works

1. On upload, a document is loaded (`pypdf` / `python-docx` / plain text),
   split into section-aware chunks (falling back to fixed-size windows for
   long sections), embedded with `sentence-transformers/all-MiniLM-L6-v2`, and
   added to a FAISS flat inner-product index (cosine similarity on normalized
   vectors) plus a parallel BM25 index kept in memory.
2. At query time, the retriever runs both dense (FAISS) and sparse (BM25)
   search, normalizes each score set, and fuses them with a tunable `alpha`
   (`alpha=1` → pure semantic search, `alpha=0` → pure keyword search). You can
   adjust `top_k` and `alpha` live from the Chat page's settings drawer or the
   Knowledge Base Explorer.
3. A lightweight lexical-overlap heuristic (`rag/evaluator.py`) approximates
   faithfulness (how much of the answer is grounded in the retrieved context)
   and blends it with the average retrieval score into the confidence
   indicator shown under each answer.

Deleting a document triggers a full rebuild of the FAISS index and BM25
corpus from the remaining chunks, since `IndexFlatIP` doesn't support cheap
single-row deletion.

## Next steps for productionizing further

1. **Swap SQLite → PostgreSQL.** `database.py` already isolates the engine
   creation behind `DATABASE_URL`; point it at a Postgres connection string
   and drop the SQLite-only `connect_args`. Add Alembic migrations instead of
   relying on `Base.metadata.create_all`.
2. **Containerize with Docker.** Add a `Dockerfile` per service and a
   `docker-compose.yml` wiring backend, frontend, and (once migrated) Postgres
   together, with a named volume for `/data/documents` and the FAISS index.
3. **Move the vector store to a managed service.** Swap the local FAISS index
   for pgvector, Pinecone, Qdrant, or Weaviate so indexing and search survive
   redeploys and scale past a single process's memory.
4. **Harden auth.** Move the JWT out of in-memory browser state into an
   httpOnly cookie issued by the backend, add refresh-token rotation, rate
   limit `/api/auth/login`, and enforce password complexity.
5. **Deploy.** Put the backend behind a proper ASGI server (Gunicorn +
   Uvicorn workers) behind a reverse proxy (nginx/Caddy) with TLS, serve the
   built frontend (`npm run build`) as static assets from a CDN, and move
   background indexing off `BackgroundTasks` onto a real task queue
   (Celery/RQ/Arq) with retries once indexing volume grows.
