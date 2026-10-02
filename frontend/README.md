# SIH26099 Enterprise Frontend (React + TypeScript + Vite)

Enterprise user interface for CPSE Material Standardization & Harmonization.

## Architecture

- **Framework:** React 18 with TypeScript and Vite
- **Port:** `http://localhost:5173`
- **Backend Communication:** React communicates **exclusively** with the Spring Boot Backend API Gateway (`http://localhost:8080/api`).
- **Strict Decoupling:** React has zero direct connections to PostgreSQL or the Python FastAPI ML Service.

## Environment Variables

Configured via `.env` or Vite environment:

```env
VITE_API_BASE_URL=http://localhost:8080/api
```

## Running Manually

```bash
cd frontend
npm install
npm run dev
```

Open:
`http://localhost:5173`

## Building for Production

```bash
npm run build
```
Generates production bundle in `dist/`.
