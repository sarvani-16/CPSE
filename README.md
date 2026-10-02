# SIH26099 – AI-Driven Standardization & Harmonization of Material Codes Across CPSEs

[![Status: Enterprise Decoupled](https://img.shields.io/badge/Architecture-4--Tier_Decoupled-blue.svg)](https://github.com)
[![Spring Boot](https://img.shields.io/badge/Spring_Boot-3.3.4-brightgreen.svg)](https://spring.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-ML_Service-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18_Vite_TS-blue.svg)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16_Enterprise-blue.svg)](https://www.postgresql.org)
[![Security: Clean](https://img.shields.io/badge/Security-Redacted_Audit_Log-critical.svg)](#15-provenance-and-data-governance-limitations)

---

> ### ⚠️ Mandatory Benchmark & Prototype Data Disclaimer
> **The current Kaggle dataset is used strictly as an algorithmic development benchmark. Real CPSE material-master data is expected to be provided by participating CPSEs.**
>
> * Ingested ONGC and BHEL demonstration records are manually constructed **Demonstration CPSE Data (Synthetic)**.
> * Generated codes (`NMM-000001` through `NMM-000008`+) are strictly **Prototype Common Material Codes** (*National Material Master* prototype identifier series) for demonstrating cross-catalog harmonization. They are **not** official government material codes.
> * No real proprietary enterprise data has been invented or claimed.

---

## 1. Project Overview

Central Public Sector Enterprises (CPSEs) under various ministries of the Government of India (e.g., ONGC, BHEL, IOCL, NTPC, SAIL, GAIL) manage extensive capital procurement pipelines. However, each enterprise independently catalogs materials using disparate item codification schemes, differing naming conventions, localized abbreviations, and divergent Units of Measure (UOM).

**SIH26099** resolves this catalog proliferation through a 4-tier enterprise harmonization platform that:
- Ingests diverse CPSE catalogs (CSV/XLSX) and auto-detects column schemas.
- Preserves original CPSE material codes permanently for end-to-end traceability.
- Executes an ensemble AI matching pipeline (Dense Semantic Embeddings + TF-IDF Lexical + RapidFuzz) with domain guardrails that prevent false matches on conflicting specifications (e.g. SS304 vs SS316).
- Supports dynamic canonical code generation (`NMM Series`) for previously unseen materials.
- Provides a certified **Human-in-the-Loop Review Center** with multi-candidate batch approval.
- Enforces an immutable data governance audit trail with active secret sanitization and RFC 4180 CSV export.

---

## 2. Decoupled 4-Tier Enterprise Architecture

The platform separates user interaction, business orchestration, relational data persistence, and heavy ML model inference into dedicated tiers:

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

### Strict Decoupling Rules
1. **React UI** communicates **ONLY** with Spring Boot (`http://localhost:8080/api`). It never directly accesses PostgreSQL, the Python ML service, or filesystem databases.
2. **Spring Boot Backend** acts as the central business orchestrator, managing JPA transactions, catalog uploads, review workflows, audit records, and issuing HTTP inference requests to the ML microservice.
3. **PostgreSQL** provides ACID persistence for enterprise records and audit trails.
4. **FastAPI ML Service** runs independently on port 8001, executing vector operations and returning structured similarity scores and explanation evidence.

---

## 3. Folder Structure

```
SIH26099/
│
├── frontend/                     # Tier 1: React 18 + TypeScript + Vite UI (Port 5173)
│   ├── public/
│   ├── src/
│   │   ├── components/           # Dashboard, Matching, Review, Canonical, Audit
│   │   ├── services/api.ts       # Centralized API Client (calls Spring Boot only)
│   │   ├── App.tsx               # Main enterprise dashboard layout
│   │   └── main.tsx              # React DOM entry point
│   ├── package.json
│   ├── vite.config.ts
│   └── README.md
│
├── backend/                      # Tier 2: Spring Boot 3.3.4 Backend (Port 8080)
│   ├── pom.xml                   # Maven dependencies (JPA, PostgreSQL, POI, OpenAPI)
│   ├── .env.example              # Environment variables template
│   └── src/
│       ├── main/java/com/sih/material/
│       │   ├── MaterialApplication.java
│       │   ├── config/           # CORS (Port 5173), RestClient, OpenAPI Swagger
│       │   ├── controller/       # REST Endpoints (/api/dashboard, /api/reviews, etc.)
│       │   ├── entity/           # JPA Entities (SourceMaterial, CanonicalMaterial, etc.)
│       │   ├── repository/       # Spring Data Repositories
│       │   ├── service/          # Business logic (Review, Canonical, Material, Audit)
│       │   ├── integration/      # AiService (communicates with ML port 8001)
│       │   └── exception/        # Controlled error handling
│       └── main/resources/
│           ├── application.yml   # PostgreSQL & ML Service configuration
│           └── application-h2.yml # Testing / fallback in-memory profile
│
├── ml-service/                   # Tier 4: Python FastAPI ML Microservice (Port 8001)
│   ├── app/
│   │   ├── main.py               # FastAPI entry point on port 8001
│   │   ├── api/endpoints.py      # POST /api/match, /api/extract-attributes
│   │   ├── matching/             # TF-IDF, RapidFuzz, SentenceTransformer, Guardrails
│   │   ├── normalization/        # Industrial specification text normalizer
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── services/             # Matching service layer
│   ├── models/                   # Cached dense embeddings
│   ├── requirements.txt
│   └── README.md
│
├── database/                     # Tier 3: PostgreSQL Schema & Administration
│   ├── schema.sql                # Complete 11-table DDL script with indexes
│   ├── seed_data.sql             # Pre-seeds CPSEs, NMM-000001 - NMM-000008, audit logs
│   ├── migrate_sqlite_to_pg.py   # SQLite to PostgreSQL migration script
│   └── README.md                 # pgAdmin connection & configuration guide
│
├── dataset/                      # Dataset Repositories with Provenance
│   ├── benchmark/kaggle/train.csv # Kaggle development benchmark (27,188 records)
│   ├── sample_cpse_data/         # Demonstration CPSE Data (Synthetic ONGC & BHEL)
│   └── README.md
│
├── docs/                         # Technical Architecture & API Documentation
│   └── architecture.md
│
├── tests/                        # Organized Test Suites
│   ├── ml/                       # Dedicated ML service and Python pytest suites
│   ├── backend/                  # Spring Boot JUnit 5 integration tests
│   └── frontend/
│
└── README.md
```

---

## 4. Component Setup & Manual Running Instructions

### Section 1: PostgreSQL Setup (Database Tier)
1. Ensure PostgreSQL is installed and the service is active on port `5432`.
2. Connect using **pgAdmin** or `psql`:
   - Host: `localhost`
   - Port: `5432`
   - Database: `sih26099`
3. Execute [`database/schema.sql`](database/schema.sql) to initialize tables.
4. Execute [`database/seed_data.sql`](database/seed_data.sql) to load initial prototype canonical items.
5. (Optional) Run `python database/migrate_sqlite_to_pg.py` to migrate historical data from SQLite.

### Section 2: ML Service Setup (FastAPI Microservice)
```bash
cd ml-service
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
- **Service URL:** `http://127.0.0.1:8001`
- **Swagger Docs:** `http://127.0.0.1:8001/docs`

### Section 3: Spring Boot Setup (Backend API Gateway)
```bash
cd backend
mvn spring-boot:run
```
- **Service URL:** `http://localhost:8080`
- **Health Check:** `http://localhost:8080/api/health`
- **Swagger UI:** `http://localhost:8080/swagger-ui.html`

### Section 4: Frontend Setup (React UI)
```bash
cd frontend
npm install
npm run dev
```
- **UI URL:** `http://localhost:5173`

---

## 5. Environment Variables

### Backend Configuration (`backend/.env` or shell variables)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sih26099
DB_USERNAME=postgres
DB_PASSWORD=your_pg_password
ML_SERVICE_URL=http://localhost:8001
SERVER_PORT=8080
```

### Frontend Configuration (`frontend/.env`)
```env
VITE_API_BASE_URL=http://localhost:8080/api
```

---

## 6. AI/ML Matching Engine Explanation

The matching engine employs an evidence-based ensemble with engineering domain guardrails:

| Component | Technology | Default Weight | Key Capability |
|:---|:---|:---:|:---|
| **Semantic Matching** | `sentence-transformers/all-MiniLM-L6-v2` | `0.40` | Captures deep semantic equivalence across abbreviations and synonyms |
| **Lexical Matching** | Scikit-Learn TF-IDF (Word [1,2] + Char [3,5]) | `0.30` | Alphanumeric code sensitivity (e.g. M10, 50mm, Sch 40) |
| **Fuzzy Matching** | RapidFuzz (Token Sort, Token Set, Ratio) | `0.30` | Word-order invariant matching against transposed titles |
| **Domain Guardrails** | Regex Specification Extractor | *Enforcer* | Detects critical conflicts (e.g. `SS304` vs `SS316`); forces `REVIEW` |

---

## 7. Model Verification & Controlled Test Results

Actual recorded outputs from the dedicated ML microservice:

### Test Case 1: Identical Fasteners with Minor Phrasing Differences
- **Material A:** `Hex Bolt M10 x 50 SS304`
- **Material B:** `Stainless Steel Hex Bolt M10 50mm SS304`
- **Result:** Decision: `REVIEW` / `MATCH` | Hybrid Score: `0.6425` | Semantic: `0.6582` | Lexical: `0.5843` | Fuzzy: `0.7000`

### Test Case 2: Metallurgy Specification Conflict (Domain Guardrail)
- **Material A:** `Hex Bolt M10 x 50 SS304`
- **Material B:** `Hex Bolt M10 x 50 SS316`
- **Result:** Decision: `REVIEW` (Demoted) | Hybrid Score: `0.8350` | Conflicts: `['ss304 vs ss316']`
- **Significance:** Text similarity is high ($83.5\%$), but the domain guardrail safely blocks automatic `MATCH` because `SS304` and `SS316` have different acid-resistance properties.

### Test Case 3: Completely Unrelated Materials
- **Material A:** `Hex Bolt M10 x 50 SS304`
- **Material B:** `Centrifugal Water Pump 5HP`
- **Result:** Decision: `NOT_MATCH` | Hybrid Score: `0.0775`

---

## 8. Automated Test Execution

### Running Python ML & Regression Tests
```bash
# Full regression suite across all 10 legacy modules
py -m pytest test_step2.py test_step3.py test_step4.py test_step5.py test_step6.py test_dashboard.py test_audit.py test_dynamic_canonical.py test_audit_export.py test_batch_review.py -v

# Dedicated ML Microservice test suite
py -m pytest tests/ml/test_ml_service.py -v

# Enterprise Governance & Audit Verification
py test_audit.py
```

### Running Spring Boot Tests
```bash
cd backend
mvn test
```

### Running Frontend Production Build Check
```bash
cd frontend
npm run build
```

---

## 9. Troubleshooting & Common Questions

1. **What if PostgreSQL is not running locally?**
   - The Spring Boot backend includes an H2 profile (`spring.profiles.active=h2`) for development without a live PostgreSQL instance. Run `mvn spring-boot:run -Dspring-boot.run.profiles=h2`.
2. **What happens if the ML microservice (Port 8001) is offline?**
   - Spring Boot catches connection errors and returns a controlled `503 Service Unavailable` with message: `"AI matching service is currently unavailable. Please ensure the Python ML microservice is running on http://localhost:8001"`. Python stack traces are never leaked to the UI.
3. **Where are the legacy SQLite databases?**
   - `outputs/analysis/materials.db` and `outputs/analysis/cpse_master.db` remain preserved as reference and benchmark data.

---

## 10. Provenance and Data Governance Limitations

1. **Benchmark Data:** The Kaggle dataset is an algorithmic benchmark for developmental scoring only.
2. **Synthetic Demonstration Data:** All ONGC and BHEL records in the review queue are synthetic prototypes.
3. **Prototype Codification:** `NMM Series` codes are algorithmic prototypes and not official government codifications.
4. **Secret Sanitization:** All audit log entries, CSV exports, and payloads are recursively scrubbed of passwords, tokens, and credentials (`[REDACTED_CONFIDENTIAL]`).
