# SIH26099 Enterprise Database Architecture (PostgreSQL + pgAdmin)

## Overview

The enterprise persistent data layer for the SIH26099 CPSE Material Harmonization Platform is hosted on **PostgreSQL**.
The database schema models all participating CPSE enterprise catalogs, raw source materials, AI match candidates, human reviews, canonical national material codes (NMM Series), permanent data governance mappings, and immutable audit logs.

> **Data Migration Status:**
> SQLite (`outputs/analysis/materials.db` and `outputs/analysis/cpse_master.db`) is currently retained as legacy/reference data during the PostgreSQL enterprise migration.

---

## 1. Local Database Configuration

| Property | Value / Source |
|:---|:---|
| **Host** | `localhost` / `127.0.0.1` |
| **Port** | `5432` |
| **Database Name** | `sih26099` |
| **Username** | `${DB_USERNAME:-postgres}` (Configured via environment variable) |
| **Password** | `${DB_PASSWORD}` (Configured via environment variable - NEVER hardcoded) |

---

## 2. Setting Up PostgreSQL with pgAdmin

### Step 1: Create the Database in PostgreSQL / pgAdmin
1. Launch **pgAdmin** or open your terminal `psql` shell.
2. Connect to your PostgreSQL server instance (`localhost:5432`).
3. Right-click on **Databases** $\rightarrow$ **Create** $\rightarrow$ **Database...**
4. Enter Database name: `sih26099` and click **Save**.

Or execute in SQL Query Tool / `psql`:
```sql
CREATE DATABASE sih26099 WITH OWNER postgres ENCODING 'UTF8';
```

### Step 2: Apply the Schema and Seed Data
In pgAdmin:
1. Select the `sih26099` database.
2. Open **Tools** $\rightarrow$ **Query Tool**.
3. Open and execute [`database/schema.sql`](schema.sql) to create all 11 tables and performance indexes.
4. Open and execute [`database/seed_data.sql`](seed_data.sql) to insert initial CPSE organizations, user roles, taxonomy classes, and prototype canonical materials (`NMM-000001` through `NMM-000008`).

### Step 3: Inspect Tables in pgAdmin
In pgAdmin Object Explorer, navigate to:
`Servers` $\rightarrow$ `PostgreSQL` $\rightarrow$ `Databases` $\rightarrow$ `sih26099` $\rightarrow$ `Schemas` $\rightarrow$ `public` $\rightarrow$ `Tables`.

Verify the presence of:
- `users`
- `cpse`
- `taxonomy`
- `source_materials`
- `material_attributes`
- `canonical_materials`
- `material_mappings`
- `match_candidates`
- `reviews`
- `processing_jobs`
- `audit_logs`

---

## 3. Migrating Data from Existing SQLite to PostgreSQL

To populate PostgreSQL with historical audit logs and demonstration CPSE records:
```bash
# Set credentials (optional if defaults are standard)
set DB_HOST=localhost
set DB_PORT=5432
set DB_NAME=sih26099
set DB_USERNAME=postgres
set DB_PASSWORD=your_local_password

# Run migration script
python database/migrate_sqlite_to_pg.py
```
