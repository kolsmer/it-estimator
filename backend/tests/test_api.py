from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_project_routes_use_repository_data(monkeypatch):
    from backend.app.api.handlers import projects

    project = {
        'id': '1',
        'name': 'Task Tracker',
        'project_name': 'Task Tracker',
        'client': 'web_app',
        'status': 'active',
        'hours': 8,
        'cost': 100000,
        'team_size': 3,
    }

    monkeypatch.setattr(projects, 'list_active_projects', lambda: [project])
    monkeypatch.setattr(projects, 'list_archived_projects', lambda: [{**project, 'status': 'archived'}])
    monkeypatch.setattr(projects, 'get_project', lambda project_id: project if project_id == 1 else None)

    active_response = client.get('/projects')
    archived_response = client.get('/projects/archived')
    detail_response = client.get('/projects/1')
    missing_response = client.get('/projects/999')

    assert active_response.status_code == 200
    assert active_response.json()[0]['name'] == 'Task Tracker'
    assert archived_response.status_code == 200
    assert archived_response.json()[0]['status'] == 'archived'
    assert detail_response.status_code == 200
    assert detail_response.json()['id'] == '1'
    assert missing_response.status_code == 404


def test_project_export_json_and_invalid_format(monkeypatch):
    from backend.app.api.handlers import projects

    project = {'id': '7', 'name': 'Exported project', 'cost': 12345}
    monkeypatch.setattr(projects, 'get_project', lambda project_id: project if project_id == 7 else None)

    response = client.get('/projects/7/export?format=json')
    invalid_response = client.get('/projects/7/export?format=xml')

    assert response.status_code == 200
    assert response.headers['content-type'].startswith('application/json')
    assert json.loads(response.text)['name'] == 'Exported project'
    assert invalid_response.status_code == 400


def test_project_actions_return_expected_statuses(monkeypatch):
    from backend.app.api.handlers import projects

    project = {'id': '3', 'name': 'Archived project'}
    monkeypatch.setattr(projects, 'archive_project', lambda project_id: project if project_id == 3 else None)
    monkeypatch.setattr(projects, 'restore_project', lambda project_id: project if project_id == 3 else None)
    monkeypatch.setattr(projects, 'delete_project', lambda project_id: project_id == 3)

    assert client.post('/projects/3/archive').json()['success'] is True
    assert client.post('/projects/3/restore').json()['success'] is True
    assert client.delete('/projects/3').json()['success'] is True
    assert client.post('/projects/404/archive').status_code == 404
    assert client.post('/projects/404/restore').status_code == 404
    assert client.delete('/projects/404').status_code == 404


def test_analyze_endpoint_runs_pipeline_without_real_llm_or_db(monkeypatch):
    from backend.app.api.handlers import analysis

    saved = {}
    project_data = {
        'project_name': 'Task app',
        'project_type': 'web_app',
        'features': [{'name': 'auth'}, {'name': 'tasks'}],
        'deadline_weeks': 8,
    }
    estimate = {
        'project_name': 'Task app',
        'project_type': 'web_app',
        'total_cost_rub': 250000,
        'duration_weeks': 8,
        'team_size': 3,
    }

    class FakeFacade:
        def __init__(self, config_path: str):
            self.config_path = config_path

        def estimate_from_ai_input(self, data: dict):
            assert data == project_data
            return {'success': True, 'data': estimate}

    monkeypatch.setattr(analysis, 'extract_project_data', lambda text: project_data)
    monkeypatch.setattr(analysis, 'EstimationFacade', FakeFacade)
    monkeypatch.setattr(analysis, 'create_prompt', lambda data, result: 'prompt')
    monkeypatch.setattr(analysis, 'get_llm_response', lambda prompt: 'LLM analysis')
    monkeypatch.setattr(
        analysis,
        'save_to_db',
        lambda data, result, llm: saved.update({'data': data, 'estimate': result, 'llm': llm}),
    )

    response = client.post('/analyze', json={'text': 'Нужно приложение для задач'})

    assert response.status_code == 200
    assert response.json()['success'] is True
    assert response.json()['llm'] == 'LLM analysis'
    assert saved['estimate'] == estimate


def test_rates_endpoint_delegates_to_settings_service(monkeypatch):
    from backend.app.api.handlers import settings

    monkeypatch.setattr(settings, 'get_rates_data', lambda: {'currency': 'RUB', 'rates': {'dev': {'middle': 2000}}})
    monkeypatch.setattr(
        settings,
        'update_rate_data',
        lambda payload: {'success': True, 'role': payload.role, 'seniority': payload.seniority, 'rate': payload.rate},
    )

    rates_response = client.get('/settings/rates')
    update_response = client.put('/settings/rates', json={'role': 'dev', 'seniority': 'middle', 'rate': 2500})

    assert rates_response.status_code == 200
    assert rates_response.json()['currency'] == 'RUB'
    assert update_response.status_code == 200
    assert update_response.json()['rate'] == 2500
