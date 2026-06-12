# PatentScout AI Task Roadmap

## Phase 0 — Workspace Setup & Scaffolding
- [x] Create folder structure (`backend/`, `frontend/`)
- [x] Initialize Python virtual environment inside `backend/`
- [x] Write `requirements.txt` with all backend dependencies
- [x] Install backend dependencies
- [x] Create `.env` template and set up configurations
- [x] Initialize frontend structure using Vite
- [x] Create docker-compose.yml for PostgreSQL
- [x] Create backend/database/test_connection.py for database checks

## Phase 1 — Data Ingestion & Retrieval (RAG)
- [x] Create `backend/ingestion/research_fetcher.py` (arXiv & Semantic Scholar)
- [x] Create `backend/ingestion/patent_fetcher.py` (PatentsView)
- [x] Create `backend/ingestion/vector_store.py` (ChromaDB + pure-Python fallback)
- [x] Verify ingestion and RAG with mock/live test queries
- [x] Implement `backend/models/pipeline.py` (AgentState TypedDict)
- [x] Implement `backend/models/pydantic_models.py` (Paper, Patent, summaries, and outputs)
- [x] Implement unit tests:
  - [x] `backend/tests/test_research_fetcher.py`
  - [x] `backend/tests/test_patent_fetcher.py`
  - [x] `backend/tests/test_embedder.py`
  - [x] `backend/tests/test_retriever.py`
- [x] Implement final integration test:
  - [x] `backend/tests/test_integration.py` (Smart Agriculture end-to-end foundation flow)

## OpenAlex Ingestion Integration
- [x] Configure `OPENALEX_API_EMAIL` in `.env.example`, `backend/config/settings.py`, and `.env`
- [x] Implement abstract reconstruction helper `reconstruct_abstract` in `backend/services/research_fetcher.py`
- [x] Implement `fetch_openalex_papers` in `backend/services/research_fetcher.py`
- [x] Update `fetch_all_papers` in `backend/services/research_fetcher.py` to aggregate all three sources with error handling and deduplication
- [x] Clean up `backend/rag/research_fetcher.py`
- [x] Refactor `backend/agents/research_agent.py` to call `fetch_papers` once and remove duplicate fetch logic
- [x] Implement OpenAlex unit test in `backend/tests/test_openalex_fetcher.py`
- [x] Update `backend/tests/verify_research_agent_live.py` to print source statistics
- [x] Run verification tests and execute live run

## Phase 2 — Multi-Agent Design
- [x] Define shared state in `backend/pipeline.py`
- [x] Build Agent 01: Research Agent (`backend/agents/research_agent.py`)
- [x] Build Agent 02: Patent Agent (`backend/agents/patent_agent.py`)
- [/] Build Agent 03: Gap Analysis Agent (`backend/agents/gap_analysis_agent.py`)
  - [ ] Create prompt template `backend/prompts/gap_analysis_agent.txt`
  - [ ] Implement core agent in `backend/agents/gap_analysis_agent.py`
  - [ ] Build unit and integration tests in `backend/tests/test_gap_analysis_agent.py`
- [ ] Build Agent 04: Innovation Agent (`backend/agents/innovation_agent.py`)
- [ ] Build Agent 05: Patentability Agent (`backend/agents/patentability_agent.py`)
- [ ] Build Agent 06: Report Generation Agent (`backend/agents/report_gen_agent.py`)

## Phase 3 — LangGraph Pipeline Compilation
- [ ] Set up LangGraph StateGraph workflow structure in `backend/agents/workflow.py`
- [ ] Implement parallel fan-out/fan-in for Agent 01 and Agent 02
- [ ] Create command-line interface (CLI) script (`backend/cli.py`) to run pipeline end-to-end

## Phase 4 — FastAPI Backend Server
- [ ] Create FastAPI app in `backend/main.py`
- [ ] Add endpoints: POST `/api/analyze`, GET `/api/status/{job_id}`, GET `/api/report/{job_id}`
- [ ] Add live updates WebSocket: `/ws/{job_id}`
- [ ] Enable CORS middleware for local frontend development

## Phase 5 — React Frontend Dashboard
- [ ] Set up React + Vite project in `frontend/`
- [ ] Build Home Page (Search domain input & execution)
- [ ] Build Agent Trace Console (Live updates via WebSockets)
- [ ] Build Gap Heatmap Screen (Interactive grid)
- [ ] Build Innovation Recommendations (Radar / Score cards)
- [ ] Build Export Report PDF/JSON Screen

## Phase 6 — Verification & Testing
- [ ] Add unit tests using `pytest` for fetchers & agents
- [ ] Run full end-to-end pipeline verification on multiple domains
- [ ] Fine-tune LLM prompts and structured schemas

## Phase 7 — Production Deployment
- [ ] Configure docker-compose for local deployment
- [ ] Prep backend for Railway
- [ ] Prep frontend for Vercel
