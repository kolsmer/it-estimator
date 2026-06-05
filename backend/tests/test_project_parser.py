from backend.app.internal.service.project_parser import extract_project_data


def test_extract_project_data_detects_task_tracker_features():
    result = extract_project_data(
        'Нужно небольшое веб-приложение для учета задач: авторизация, '
        'создание и редактирование задач, dashboard. Срок 8 недель.'
    )

    feature_names = {feature['name'] for feature in result['features']}

    assert result['project_type'] == 'web_app'
    assert result['deadline_weeks'] == 8
    assert {'авторизация', 'управление задачами', 'dashboard'}.issubset(feature_names)
