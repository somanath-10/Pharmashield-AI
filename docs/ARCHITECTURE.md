# Architecture

PharmaShield AI uses a two-tier MVP architecture:

- Frontend: Next.js App Router, TypeScript, Tailwind CSS, React Query, Recharts.
- Backend: FastAPI, Pydantic v2, SQLAlchemy, PostgreSQL-oriented configuration, deterministic multi-agent orchestration.

Core backend flow:

1. `POST /api/cases/analyze` receives the pharmacy case.
2. The `IntentRouter` detects shortage, payer, and authenticity/compliance signals.
3. The `AgentCoordinator` runs the selected agents deterministically.
4. The RAG layer performs query expansion, hybrid retrieval, reranking, and citation shaping.
5. The `SynthesisAgent` merges outputs into a pharmacist-reviewable action plan.
6. Guardrails enforce safety language and review requirements.
7. Feedback is stored and can be promoted into scoped memory items.

Storage responsibilities:

- PostgreSQL: cases, agent runs, policies, shortages, recalls, feedback, memory.
- Qdrant: provisioned in Compose for vector search evolution; the MVP uses deterministic local vectors for reliability.
- Local object storage: uploaded documents.
- Redis: included for future caching and task coordination.
