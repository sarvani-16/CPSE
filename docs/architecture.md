# SIH26099 Enterprise Architecture Documentation

## 1. 4-Tier Enterprise Architecture Overview

The system is decoupled into four dedicated tiers to support scalability, high-performance ML inference, robust transactional data governance, and an intuitive user interface:

```
                    ┌───────────────────────────────┐
                    │      React UI (Vite / TS)     │
                    │      frontend/ (Port 5173)    │
                    └───────────────┬───────────────┘
                                    │
                               REST / JSON
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      Spring Boot 3.3 Backend  │
                    │      backend/ (Port 8080)     │
                    └───────────────┬───────┬───────┘
                                    │       │
                      Spring JPA    │       │ HTTP / JSON
                                    │       │
                                    ▼       ▼
                    ┌──────────────────┐  ┌──────────────────────────────┐
                    │   PostgreSQL     │  │   Python FastAPI ML Service  │
                    │   sih26099 (5432)│  │   ml-service/ (Port 8001)    │
                    └──────────────────┘  └──────────────┬───────────────┘
                                                         │
                                                         ▼
                                          ┌──────────────────────────────┐
                                          │   AI / ML Ensemble Models    │
                                          │   - MiniLM Dense Embeddings  │
                                          │   - TF-IDF Word/Char N-Grams │
                                          │   - RapidFuzz Token Matchers │
                                          │   - Domain Conflict Demotion │
                                          └──────────────────────────────┘
```

---

## 2. Decoupled Component Responsibilities

### Tier 1: Frontend (`frontend/`)
- **Port:** `5173`
- **Tech:** React 18, Vite, TypeScript.
- **Responsibility:** User presentation, data visualization, interactive review queue, multi-factor audit filters.
- **Rule:** Communicates **exclusively** with Spring Boot (`http://localhost:8080/api`). Never accesses PostgreSQL or FastAPI directly.

### Tier 2: Backend API Gateway (`backend/`)
- **Port:** `8080`
- **Tech:** Java 17, Spring Boot 3.3.4, Spring Data JPA, Apache POI, Commons CSV.
- **Responsibility:**
  - REST API contracts for the UI.
  - Multi-tenant catalog ingestion (CSV/XLSX) and column synonym mapping.
  - Human-in-the-Loop review queue state management (Approval, Rejection, Batch Actions).
  - Dynamic canonical material creation (NMM Series) with idempotency.
  - Immutable audit logging with active credential sanitization and RFC 4180 CSV export.
  - Orchestration of ML inference calls to the FastAPI microservice.

### Tier 3: Database & Administration (`database/`)
- **Port:** `5432`
- **Tech:** PostgreSQL (`sih26099`), pgAdmin.
- **Responsibility:** Relational persistence for CPSE enterprises, source materials, mappings, canonical items, reviews, and audit logs.
- **Note:** SQLite (`outputs/analysis/cpse_master.db`) is preserved as legacy reference.

### Tier 4: AI/ML Microservice (`ml-service/`)
- **Port:** `8001`
- **Tech:** Python 3.14 / 3.11+, FastAPI, SentenceTransformers, Scikit-Learn, RapidFuzz.
- **Responsibility:**
  - Dense embedding generation (`sentence-transformers/all-MiniLM-L6-v2`).
  - TF-IDF character and word n-gram lexical vectorization.
  - RapidFuzz token set and sort ratio string similarity.
  - Rule-based technical token conflict detection and automatic demotion.
  - Evidence-based explanation generation.
