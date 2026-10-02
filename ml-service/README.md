# SIH26099 Dedicated AI/ML Service

Dedicated microservice for CPSE material code standardization, semantic matching, and technical domain guardrail enforcement.

## Architecture

- **Semantic Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **Lexical Model:** Scikit-Learn TF-IDF (word n-grams [1,2] + character n-grams [3,5])
- **Fuzzy Model:** RapidFuzz (token set ratio, token sort ratio, partial ratio)
- **Domain Guardrails:** Rule-based technical token extractor with strict conflict demotion (e.g., SS304 vs SS316 metallurgy mismatch)
- **Framework:** FastAPI with Uvicorn

## Default Port & URL

- **URL:** `http://127.0.0.1:8001`
- **Swagger Documentation:** `http://127.0.0.1:8001/docs`

## Endpoints

- `POST /api/match`: AI Hybrid material comparison (returns decision `MATCH`, `REVIEW`, `NOT_MATCH`, scores, and explanation)
- `POST /api/batch-match`: Batched comparison of material pairs
- `POST /api/extract-attributes`: Text normalization and dimensional/grade attribute extraction
- `GET /api/candidates/{posting_id}`: Retrieve top K candidate matches from benchmark catalog
- `GET /api/health`: Service health and model status

## Running Manually

```bash
cd ml-service
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
