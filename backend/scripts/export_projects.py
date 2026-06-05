#!/usr/bin/env python3
import csv
import json
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd
import psycopg
import xlwt
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import DATABASE_URL
from backend.app.internal.repository.migrations import run_migrations


def serialize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def fetch_projects():
    run_migrations()
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        rows = conn.execute(
            '''
            SELECT id, project_name, project_type, total_cost_rub, duration_weeks,
                   team_size, generated_at, input_project, estimation, llm_analysis
            FROM projects
            ORDER BY generated_at DESC
            '''
        ).fetchall()
    return [{key: serialize_value(value) for key, value in row.items()} for row in rows]


def export_json(path: Path, projects):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)


def export_csv(path: Path, projects):
    if not projects:
        return
    keys = projects[0].keys()
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for p in projects:
            writer.writerow(p)


def export_excel(path: Path, projects):
    df = pd.DataFrame(projects)
    df.to_excel(path, index=False)


def export_xls(path: Path, projects):
    if not projects:
        return
    headers = list(projects[0].keys())
    wb = xlwt.Workbook()
    ws = wb.add_sheet('projects')
    for col, header in enumerate(headers):
        ws.write(0, col, header)
    for row_idx, project in enumerate(projects, start=1):
        for col_idx, header in enumerate(headers):
            ws.write(row_idx, col_idx, str(project.get(header, '')))
    wb.save(str(path))


def main():
    out = PROJECT_ROOT
    projects = fetch_projects()
    export_json(out / 'projects_export.json', projects)
    export_csv(out / 'projects_export.csv', projects)
    export_excel(out / 'projects_export.xlsx', projects)
    export_xls(out / 'projects_export.xls', projects)

    print('Exported', len(projects), 'projects to JSON/CSV/XLSX')


if __name__ == '__main__':
    main()
