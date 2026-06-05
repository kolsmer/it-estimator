from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row

from backend.app.core.config import DATABASE_URL
from backend.app.internal.repository.migrations import run_migrations


PROJECT_TABLE = 'projects'
ARCHIVE_TABLE = 'projects_archive'


def _connect() -> psycopg.Connection:
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def _to_api_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: _to_api_value(value) for key, value in row.items()}


def ensure_project_table() -> None:
    run_migrations()


def ensure_archive_table() -> None:
    run_migrations()


def init_db() -> None:
    run_migrations()
    print('База данных PostgreSQL инициализирована')


def _fetch_row(table: str, project_id: int) -> dict[str, Any] | None:
    with _connect() as conn:
        row = conn.execute(f'SELECT * FROM {table} WHERE id = %s', (project_id,)).fetchone()
    return _normalize_row(row) if row else None


def _row_to_project(row: dict[str, Any], status: str) -> dict[str, Any]:
    project = dict(row)
    project['id'] = str(project.get('id'))
    project['status'] = status
    project['name'] = project.get('project_name') or project.get('name') or 'Без названия'
    project['client'] = project.get('project_type') or project.get('client') or '—'
    project['hours'] = project.get('duration_weeks') or project.get('hours') or 0
    project['cost'] = project.get('total_cost_rub') or project.get('cost') or 0
    project['team_size'] = project.get('team_size') or 0
    project['generated_at'] = project.get('generated_at') or ''
    return project


def list_active_projects() -> list[dict[str, Any]]:
    run_migrations()
    with _connect() as conn:
        rows = conn.execute(
            f'''
            SELECT id, project_name, project_type, total_cost_rub,
                   duration_weeks, team_size, generated_at
            FROM {PROJECT_TABLE}
            ORDER BY generated_at DESC
            '''
        ).fetchall()

    return [
        {
            'id': str(row['id']),
            'name': row['project_name'] or 'Без названия',
            'client': row['project_type'] or '—',
            'status': 'active',
            'hours': row['duration_weeks'] or 0,
            'cost': _to_api_value(row['total_cost_rub']) or 0,
            'team_size': row['team_size'] or 0,
            'generated_at': _to_api_value(row['generated_at']) or '',
        }
        for row in rows
    ]


def get_project(project_id: int) -> dict[str, Any] | None:
    run_migrations()
    active = _fetch_row(PROJECT_TABLE, project_id)
    if active:
        return _row_to_project(active, 'active')

    archived = _fetch_row(ARCHIVE_TABLE, project_id)
    if archived:
        return _row_to_project(archived, 'archived')

    return None


def archive_project(project_id: int) -> dict[str, Any] | None:
    run_migrations()
    if not _fetch_row(PROJECT_TABLE, project_id):
        return None

    with _connect() as conn:
        with conn.transaction():
            conn.execute(f'DELETE FROM {ARCHIVE_TABLE} WHERE id = %s', (project_id,))
            conn.execute(
                f'''
                INSERT INTO {ARCHIVE_TABLE} (
                    id, project_name, project_type, total_cost_rub, duration_weeks,
                    team_size, generated_at, input_project, estimation, llm_analysis
                )
                SELECT id, project_name, project_type, total_cost_rub, duration_weeks,
                       team_size, generated_at, input_project, estimation, llm_analysis
                FROM {PROJECT_TABLE}
                WHERE id = %s
                ''',
                (project_id,),
            )
            conn.execute(f'DELETE FROM {PROJECT_TABLE} WHERE id = %s', (project_id,))

    return get_project(project_id)


def restore_project(project_id: int) -> dict[str, Any] | None:
    run_migrations()
    if not _fetch_row(ARCHIVE_TABLE, project_id):
        return None

    with _connect() as conn:
        with conn.transaction():
            conn.execute(f'DELETE FROM {PROJECT_TABLE} WHERE id = %s', (project_id,))
            conn.execute(
                f'''
                INSERT INTO {PROJECT_TABLE} (
                    id, project_name, project_type, total_cost_rub, duration_weeks,
                    team_size, generated_at, input_project, estimation, llm_analysis
                )
                SELECT id, project_name, project_type, total_cost_rub, duration_weeks,
                       team_size, generated_at, input_project, estimation, llm_analysis
                FROM {ARCHIVE_TABLE}
                WHERE id = %s
                ''',
                (project_id,),
            )
            conn.execute(f'DELETE FROM {ARCHIVE_TABLE} WHERE id = %s', (project_id,))

    return get_project(project_id)


def delete_project(project_id: int) -> bool:
    run_migrations()
    with _connect() as conn:
        with conn.transaction():
            active_result = conn.execute(f'DELETE FROM {PROJECT_TABLE} WHERE id = %s', (project_id,))
            archive_result = conn.execute(f'DELETE FROM {ARCHIVE_TABLE} WHERE id = %s', (project_id,))

    return bool(active_result.rowcount or archive_result.rowcount)


def list_archived_projects() -> list[dict[str, Any]]:
    run_migrations()
    with _connect() as conn:
        rows = conn.execute(
            f'''
            SELECT id, project_name, project_type, total_cost_rub,
                   duration_weeks, team_size, generated_at
            FROM {ARCHIVE_TABLE}
            ORDER BY generated_at DESC
            '''
        ).fetchall()

    return [
        {
            'id': str(row['id']),
            'name': row['project_name'] or 'Без названия',
            'client': row['project_type'] or '—',
            'status': 'archived',
            'hours': row['duration_weeks'] or 0,
            'cost': _to_api_value(row['total_cost_rub']) or 0,
            'team_size': row['team_size'] or 0,
            'generated_at': _to_api_value(row['generated_at']) or '',
        }
        for row in rows
    ]


def save_to_db(project_data: dict[str, Any], estimate: dict[str, Any], llm_response: str) -> None:
    run_migrations()
    with _connect() as conn:
        conn.execute(
            f'''
            INSERT INTO {PROJECT_TABLE} (
                project_name, project_type, total_cost_rub, duration_weeks,
                team_size, generated_at, input_project, estimation, llm_analysis
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''',
            (
                estimate['project_name'],
                estimate['project_type'],
                estimate['total_cost_rub'],
                estimate['duration_weeks'],
                estimate['team_size'],
                datetime.now(timezone.utc),
                json.dumps(project_data, ensure_ascii=False),
                json.dumps(estimate, ensure_ascii=False),
                llm_response,
            ),
        )
        conn.commit()
    print('Отчёт сохранён в PostgreSQL')


def show_all_project() -> None:
    run_migrations()
    with _connect() as conn:
        projects = conn.execute(
            f'SELECT id, project_name, generated_at FROM {PROJECT_TABLE} ORDER BY generated_at DESC'
        ).fetchall()

    if projects:
        print('Сохранённые проекты в БД:')
        for project in projects:
            print(f"  #{project['id']} {project['project_name']} ({project['generated_at']})")
    else:
        print('\nВ БД пусто')
