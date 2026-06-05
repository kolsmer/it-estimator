from __future__ import annotations

from pathlib import Path

import psycopg

from backend.app.core.config import DATABASE_URL


MIGRATIONS_DIR = Path(__file__).resolve().parent / 'migrations'


def run_migrations() -> None:
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            '''
        )

        applied = {
            row[0]
            for row in conn.execute('SELECT version FROM schema_migrations').fetchall()
        }

        for migration_path in sorted(MIGRATIONS_DIR.glob('*.sql')):
            version = migration_path.name
            if version in applied:
                continue

            sql = migration_path.read_text(encoding='utf-8')
            with conn.transaction():
                conn.execute(sql)
                conn.execute('INSERT INTO schema_migrations (version) VALUES (%s)', (version,))
