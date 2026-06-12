[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/s7J27iqd)

# PatentScout AI 🚀
### Agentic AI Innovation Discovery & Patent Analysis System

PatentScout AI is a multi-agent platform designed to discover innovation gaps by analyzing the academic research landscape alongside commercial patent databases. Running on **LangGraph** and powered by **Google Gemini 2.5 Flash**, the system retrieves data from multiple academic sources and queries a localized corpus of 10,791 patents to isolate commercialization opportunities.

---

## Technical Architecture

PatentScout AI utilizes a collaborative multi-agent design sharing a central `AgentState` context:

### 1. Research Agent (`backend/agents/research_agent.py`)
- **Sources**: Academic journals and articles from **arXiv**, **Semantic Scholar**, and **OpenAlex**.
- **Capabilities**: Reconstructs compressed OpenAlex inverted index abstracts, performs title-based deduplication, and groups academic literature into technology topics.
- **Verification**: `python -m backend.tests.verify_research_agent_live`

### 2. Patent Agent (`backend/agents/patent_agent.py`)
- **Source**: A verified, production-scale database of **10,791 unique patents** stored locally.
- **Capabilities**: Performs vector RAG searches using local embeddings, queries matching patents, clusters technical claims, and extracts saturated technology domains.
- **Verification**: `python -m backend.tests.verify_patent_agent_live`

### 3. Gap Analysis Agent (`backend/agents/gap_agent.py`) *(In Development)*
- **Capabilities**: Cross-references academic topics with patent clusters to isolate technology gaps (high research activity but low patent saturation).

---

## Technology Stack

- **Large Language Models**: Google Gemini 2.5 Flash (via `LangChain` Google GenAI SDK).
- **Core Orchestration**: LangGraph StateGraph pipeline, Pydantic schemas.
- **Vector Database**: ChromaDB (with pure-Python RAG memory fallbacks).
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`).
- **Data Ingestion**: Pandas, BigQuery validation tools.
- **Backend**: FastAPI.
- **Frontend**: React.js + Vite.

---

## Project Structure

```bash
PatentScout-AI/
│
├── backend/
│   ├── agents/                     # Multi-Agent nodes (Research, Patent, Gap, etc.)
│   ├── config/                     # Settings and environment variables
│   ├── data_pipeline/              # Ingestion, validation, and bootstrapping pipelines
│   ├── models/                     # Shared Pydantic data schemas and TypedDict states
│   ├── prompts/                    # System prompts templates for LLM instruction
│   ├── services/                   # Fetchers, Embedder, Retriever, and LLM clients
│   └── tests/                      # Automated unit, integration, and live verify scripts
│
├── data/
│   ├── raw_patents/                # BigQuery 11,650-patent export CSV
│   └── processed_patents/          # Balanced and validated output datasets
│
├── requirements.txt
└── README.md
```

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/SECE-24-28/final-capstone-project-agentic-ai-patents_scout_ai.git
cd final-capstone-project-agentic-ai-patents_scout_ai
```

### 2. Setup Virtual Environment (Windows)
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
OPENALEX_API_EMAIL=your_email@domain.com
```

---

## Data Ingestion Pipeline

To populate your local persistent vector database with the full 11,650 Google Patents dataset:

1. **Validate Raw Data**:
   ```powershell
   .venv\Scripts\python.exe -m backend.tests.validate_patent_csv
   ```
2. **Ingest & Embed Patents**:
   ```powershell
   .venv\Scripts\python.exe -m backend.data_pipeline.patent_ingestion
   ```
   *Note: Uses `.upsert()` to prevent duplication errors on re-runs.*

---

## Execution & Verification

To run manual verification and live RAG analyses across both agents:

### 1. Verify Research Agent
Runs a live academic search and groups findings by publisher source:
```powershell
.venv\Scripts\python.exe -m backend.tests.verify_research_agent_live
```

### 2. Verify Patent Agent
Queries the local vector store for the target domain and clusters patent classes:
```powershell
.venv\Scripts\python.exe -m backend.tests.verify_patent_agent_live
```

### 3. Run Automated Integration Test Suite
```powershell
.venv\Scripts\python.exe -m unittest backend/tests/test_patent_agent_live.py
```

---

## Authors
- **Sudharshan S**
- **Sivaganesh B**
- **Prennithe S G**
