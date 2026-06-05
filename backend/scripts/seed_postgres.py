#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import psycopg

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import DATABASE_URL
from backend.app.internal.repository.migrations import run_migrations


SEED_PROJECTS = [
    {
        'project_name': 'Demo: Веб-приложение для задач',
        'project_type': 'web_app',
        'total_cost_rub': 814500,
        'duration_weeks': 8,
        'team_size': 7,
        'input_project': {
            'project_type': 'web_app',
            'name': 'Веб-приложение',
            'description': 'Небольшой веб-сервис для учета задач: авторизация, задачи, CRUD и dashboard.',
            'features': [
                {'name': 'авторизация', 'complexity': 'medium'},
                {'name': 'управление задачами', 'complexity': 'medium'},
                {'name': 'dashboard', 'complexity': 'medium'},
                {'name': 'CRUD-операции', 'complexity': 'medium'},
            ],
            'design_complexity': 'low',
            'backend_complexity': 'medium',
            'frontend_complexity': 'medium',
            'target_platforms': ['web'],
            'integrations': [],
            'deadline_weeks': 8,
            'currency': 'RUB',
            'similar_projects_found': 0,
        },
        'estimation': {
            'total_cost_rub': 814500,
            'total_hours': 252,
            'duration_weeks': 8,
            'team_size': 7,
            'hourly_rate_avg_rub': 3232.14,
            'project_name': 'Веб-приложение',
            'project_type': 'web_app',
            'currency': 'RUB',
            'confidence_score': 0.6,
            'similar_projects_found': 0,
        },
        'llm_analysis': (
            'Суть:\n'
            '- Demo-проект веб-приложения для учета задач.\n\n'
            'Риски:\n'
            '- Сжатый срок может уменьшить запас на тестирование.\n\n'
            'Рекомендации:\n'
            '- Сначала стабилизировать авторизацию, CRUD и dashboard.\n\n'
            'Итог:\n'
            '- Подходит как стартовый проект для проверки UI и API.'
        ),
    },
    {
        'project_name': 'Demo: CRM для заявок',
        'project_type': 'crm',
        'total_cost_rub': 1260000,
        'duration_weeks': 12,
        'team_size': 6,
        'input_project': {
            'project_type': 'crm',
            'name': 'CRM-система',
            'description': 'CRM для заявок: клиенты, сделки, статусы, экспорт CSV.',
            'features': [
                {'name': 'авторизация', 'complexity': 'medium'},
                {'name': 'экспорт данных', 'complexity': 'medium'},
                {'name': 'интеграция с CRM', 'complexity': 'high'},
            ],
            'design_complexity': 'medium',
            'backend_complexity': 'high',
            'frontend_complexity': 'medium',
            'target_platforms': ['web'],
            'integrations': ['crm'],
            'deadline_weeks': 12,
            'currency': 'RUB',
            'similar_projects_found': 1,
        },
        'estimation': {
            'total_cost_rub': 1260000,
            'total_hours': 360,
            'duration_weeks': 12,
            'team_size': 6,
            'hourly_rate_avg_rub': 3500,
            'project_name': 'CRM-система',
            'project_type': 'crm',
            'currency': 'RUB',
            'confidence_score': 0.7,
            'similar_projects_found': 1,
        },
        'llm_analysis': (
            'Суть:\n'
            '- Demo-проект CRM для заявок и сделок.\n\n'
            'Риски:\n'
            '- Интеграции и экспорт могут потребовать уточнения форматов.\n\n'
            'Рекомендации:\n'
            '- Согласовать статусы заявок и права пользователей до разработки.\n\n'
            'Итог:\n'
            '- Подходит для проверки списка проектов, ролей и карточки проекта.'
        ),
    },
]


def seed() -> int:
    run_migrations()
    inserted = 0

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.transaction():
            for project in SEED_PROJECTS:
                exists = conn.execute(
                    'SELECT 1 FROM projects WHERE project_name = %s LIMIT 1',
                    (project['project_name'],),
                ).fetchone()
                if exists:
                    continue

                conn.execute(
                    '''
                    INSERT INTO projects (
                        project_name, project_type, total_cost_rub, duration_weeks,
                        team_size, generated_at, input_project, estimation, llm_analysis
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''',
                    (
                        project['project_name'],
                        project['project_type'],
                        project['total_cost_rub'],
                        project['duration_weeks'],
                        project['team_size'],
                        datetime.now(timezone.utc),
                        json.dumps(project['input_project'], ensure_ascii=False),
                        json.dumps(project['estimation'], ensure_ascii=False),
                        project['llm_analysis'],
                    ),
                )
                inserted += 1

    return inserted


def main() -> None:
    inserted = seed()
    print(f'Seeded {inserted} project(s)')


if __name__ == '__main__':
    main()
