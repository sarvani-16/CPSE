"""
SIH26099 - AI-Driven Standardization & Harmonization of Material Codes Across CPSEs
Database Migration Utility: SQLite (Legacy Reference) -> PostgreSQL (Enterprise Master)
"""

import os
import sys
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = PROJECT_ROOT / "outputs" / "analysis" / "cpse_master.db"

# PostgreSQL connection parameters (configurable via environment variables)
PG_HOST = os.getenv("DB_HOST", "localhost")
PG_PORT = os.getenv("DB_PORT", "5432")
PG_NAME = os.getenv("DB_NAME", "sih26099")
PG_USER = os.getenv("DB_USERNAME", "postgres")
PG_PASSWORD = os.getenv("DB_PASSWORD", "")


def migrate_data():
    print("=" * 70)
    print("SIH26099 Database Migration: SQLite -> PostgreSQL")
    print("=" * 70)
    print(f"Source SQLite DB: {SQLITE_DB}")
    print(f"Target PostgreSQL: {PG_USER}@{PG_HOST}:{PG_PORT}/{PG_NAME}")

    if not SQLITE_DB.exists():
        print(f"[!] Source SQLite database not found at {SQLITE_DB}")
        return

    try:
        import psycopg2
    except ImportError:
        print("[!] psycopg2 or psycopg2-binary not installed.")
        print("    To run migration: pip install psycopg2-binary")
        print("    SQLite database is safely preserved as legacy reference.")
        return

    try:
        pg_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            dbname=PG_NAME,
            user=PG_USER,
            password=PG_PASSWORD,
        )
        pg_cur = pg_conn.cursor()
        print("[+] Connected to PostgreSQL successfully.")
    except Exception as e:
        print(f"[!] PostgreSQL connection failed: {e}")
        print("    Please ensure PostgreSQL service is active and database 'sih26099' exists.")
        return

    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # 1. Migrate Canonical Materials
    try:
        sqlite_cur.execute("SELECT * FROM canonical_materials")
        rows = sqlite_cur.fetchall()
        print(f"[*] Migrating {len(rows)} canonical materials...")
        for r in rows:
            pg_cur.execute(
                """
                INSERT INTO canonical_materials (
                    national_material_code, canonical_code, standardized_description,
                    canonical_description, category, material_type, standard_specification,
                    standard_uom, approval_status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (national_material_code) DO UPDATE SET
                    standardized_description = EXCLUDED.standardized_description,
                    canonical_description = EXCLUDED.canonical_description;
                """,
                (
                    r["national_material_code"],
                    r["canonical_code"],
                    r["standardized_description"],
                    r["canonical_description"],
                    r["category"],
                    r["material_type"],
                    r["standard_specification"],
                    r["standard_uom"],
                    r["approval_status"] or "APPROVED",
                    r["created_at"],
                ),
            )
        pg_conn.commit()
        print(f"[+] Canonical materials migrated successfully.")
    except Exception as e:
        print(f"[!] Error migrating canonical materials: {e}")
        pg_conn.rollback()

    # 2. Migrate Source Materials
    try:
        sqlite_cur.execute("SELECT * FROM source_materials")
        rows = sqlite_cur.fetchall()
        print(f"[*] Migrating {len(rows)} source materials...")
        for r in rows:
            pg_cur.execute(
                """
                INSERT INTO source_materials (
                    cpse_name, material_code, description, specification,
                    material_type, material_grade, dimensions, unit_of_measure,
                    manufacturer, part_number, category, source_file, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (cpse_name, material_code) DO NOTHING;
                """,
                (
                    r["cpse_name"],
                    r["material_code"],
                    r["description"],
                    r["specification"],
                    r["material_type"],
                    r["material_grade"],
                    r["dimensions"],
                    r["unit_of_measure"],
                    r["manufacturer"],
                    r["part_number"],
                    r["category"],
                    r["source_file"],
                    r["created_at"],
                ),
            )
        pg_conn.commit()
        print(f"[+] Source materials migrated successfully.")
    except Exception as e:
        print(f"[!] Error migrating source materials: {e}")
        pg_conn.rollback()

    # 3. Migrate Material Mappings
    try:
        sqlite_cur.execute("SELECT * FROM material_mappings")
        rows = sqlite_cur.fetchall()
        print(f"[*] Migrating {len(rows)} material mappings...")
        for r in rows:
            # Resolve foreign key ID in postgres
            pg_cur.execute(
                "SELECT id FROM source_materials WHERE cpse_name = %s AND material_code = %s",
                (r["cpse_name"], r["original_material_code"]),
            )
            src_row = pg_cur.fetchone()
            if src_row:
                pg_cur.execute(
                    """
                    INSERT INTO material_mappings (
                        source_material_id, cpse_name, original_material_code,
                        original_description, canonical_material_code, canonical_description,
                        match_status, confidence, reviewer, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        src_row[0],
                        r["cpse_name"],
                        r["original_material_code"],
                        r["original_description"],
                        r["canonical_material_code"],
                        r["canonical_description"],
                        r["match_status"],
                        r["confidence"],
                        r["reviewer"],
                        r["timestamp"],
                    ),
                )
        pg_conn.commit()
        print(f"[+] Material mappings migrated successfully.")
    except Exception as e:
        print(f"[!] Error migrating material mappings: {e}")
        pg_conn.rollback()

    # 4. Migrate Audit Logs
    try:
        sqlite_cur.execute("SELECT * FROM audit_logs")
        rows = sqlite_cur.fetchall()
        print(f"[*] Migrating {len(rows)} audit logs...")
        for r in rows:
            pg_cur.execute(
                """
                INSERT INTO audit_logs (
                    action, entity_type, entity_id, old_value, new_value,
                    performed_by, timestamp, reason, "user"
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    r["action"],
                    r["entity_type"],
                    r["entity_id"],
                    r["old_value"],
                    r["new_value"],
                    r["performed_by"],
                    r["timestamp"],
                    r["reason"],
                    r["user"],
                ),
            )
        pg_conn.commit()
        print(f"[+] Audit logs migrated successfully.")
    except Exception as e:
        print(f"[!] Error migrating audit logs: {e}")
        pg_conn.rollback()

    sqlite_conn.close()
    pg_conn.close()
    print("=" * 70)
    print("MIGRATION COMPLETED TO POSTGRESQL!")
    print("=" * 70)


if __name__ == "__main__":
    migrate_data()
