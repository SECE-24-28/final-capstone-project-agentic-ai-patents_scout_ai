# PatentScout AI: Setup & Configuration Guide

This guide walks you through setting up the virtual environment, starting the database, and running the validation suite for the **PatentScout AI** foundation layer.

---

## 🛠️ Step 1: Virtual Environment Setup

Inside the root directory, create and activate a Python virtual environment:

### In PowerShell:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
```

### In Git Bash / Linux:
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/Scripts/activate
```

---

## 📦 Step 2: Install Dependencies

With the virtual environment activated, install all backend packages:

```bash
pip install -r backend/requirements.txt
```

---

## 🐋 Step 3: Start PostgreSQL Container

Launch the database service defined in `docker-compose.yml`:

```bash
docker compose up -d
```

Verify that the container is running:
```bash
docker ps
```

---

## 🧪 Step 4: Run Foundation Verification Tests

Execute the test suites to validate fetching, embedding, and retriever performance:

### Set PYTHONPATH
To make sure imports work correctly:
```powershell
# In PowerShell:
$env:PYTHONPATH="."
```
```bash
# In Bash:
export PYTHONPATH="."
```

### Run Individual Unit Tests
```bash
python -m unittest backend/tests/test_research_fetcher.py
python -m unittest backend/tests/test_patent_fetcher.py
python -m unittest backend/tests/test_embedder.py
python -m unittest backend/tests/test_retriever.py
```

### Run End-to-End Foundation Integration Test
```bash
python -m unittest backend/tests/test_integration.py
```
