#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import DATABASE_URL, ESTIMATOR_CONFIG_PATH
from backend.app.internal.repository.migrations import run_migrations
from backend.app.internal.service.estimation_service import EstimationFacade
from backend.app.internal.service.llm_service import create_prompt, get_llm_response
from backend.app.internal.service.project_parser import extract_project_data


def regenerate_project(project_id: int, recompute_estimate: bool) -> dict:
    run_migrations()
    conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    row = conn.execute(
        'SELECT id, input_project, estimation FROM projects WHERE id = %s',
        (project_id,),
    ).fetchone()
    if not row:
        conn.close()
        raise SystemExit(f'Project #{project_id} not found')

    input_project = json.loads(row['input_project'])
    estimate = json.loads(row['estimation'])

    if recompute_estimate:
        source_text = input_project.get('description', '')
        input_project = extract_project_data(source_text)
        result = EstimationFacade(str(ESTIMATOR_CONFIG_PATH)).estimate_from_ai_input(input_project)
        if not result.get('success'):
            conn.close()
            raise SystemExit(result.get('error', 'Estimation failed'))
        estimate = result['data']

    prompt = create_prompt(input_project, estimate)
    llm_analysis = get_llm_response(prompt) or 'Не удалось получить ответ от языковой модели.'

    conn.execute(
        '''
        UPDATE projects
        SET project_name = %s,
            project_type = %s,
            total_cost_rub = %s,
            duration_weeks = %s,
            team_size = %s,
            generated_at = %s,
            input_project = %s,
            estimation = %s,
            llm_analysis = %s
        WHERE id = %s
        ''',
        (
            estimate['project_name'],
            estimate['project_type'],
            estimate['total_cost_rub'],
            estimate['duration_weeks'],
            estimate['team_size'],
            datetime.now(timezone.utc),
            json.dumps(input_project, ensure_ascii=False),
            json.dumps(estimate, ensure_ascii=False),
            llm_analysis,
            project_id,
        ),
    )
    conn.commit()
    conn.close()

    return {
        'id': project_id,
        'project_name': estimate['project_name'],
        'project_type': estimate['project_type'],
        'total_cost_rub': estimate['total_cost_rub'],
        'duration_weeks': estimate['duration_weeks'],
        'llm_analysis': llm_analysis,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Regenerate project estimation and LLM analysis.')
    parser.add_argument('project_id', type=int)
    parser.add_argument(
        '--llm-only',
        action='store_true',
        help='Keep stored input/estimate and regenerate only llm_analysis.',
    )
    args = parser.parse_args()

    result = regenerate_project(args.project_id, recompute_estimate=not args.llm_only)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
