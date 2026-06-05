import re
from typing import Any


PROJECT_TYPE_NAMES = {
    'website': 'Веб-сайт',
    'web_app': 'Веб-приложение',
    'mobile_app': 'Мобильное приложение',
    'ecommerce': 'Интернет-магазин',
    'marketplace': 'Маркетплейс',
    'crm': 'CRM-система',
    'erp': 'ERP-система',
    'api': 'Backend API',
    'chatbot': 'Чат-бот',
    'ai_service': 'AI-сервис',
    'other': 'IT-проект',
}


PROJECT_TYPE_RULES: dict[str, list[tuple[str, int]]] = {
    'ai_service': [
        ('ai', 3),
        ('ml', 3),
        ('llm', 3),
        ('нейросет', 4),
        ('искусственн', 4),
        ('машинн', 4),
        ('model', 2),
        ('модель', 2),
        ('прогноз', 3),
        ('распознавание', 3),
        ('data science', 4),
    ],
    'crm': [
        ('crm', 5),
        ('клиент', 2),
        ('сделк', 4),
        ('воронк', 4),
        ('лид', 3),
        ('amocrm', 5),
    ],
    'erp': [
        ('erp', 5),
        ('1с', 4),
        ('склад', 3),
        ('остатк', 3),
        ('товар', 2),
        ('закупк', 2),
        ('ресурс', 2),
        ('производств', 3),
    ],
    'ecommerce': [
        ('интернет-магазин', 5),
        ('магазин', 3),
        ('корзин', 4),
        ('каталог', 3),
        ('оплат', 3),
        ('заказ', 2),
        ('товар', 2),
    ],
    'marketplace': [
        ('маркетплейс', 5),
        ('продавц', 4),
        ('покупател', 4),
        ('витрин', 2),
        ('комисси', 2),
    ],
    'mobile_app': [
        ('мобильн', 5),
        ('ios', 4),
        ('android', 4),
        ('app store', 3),
        ('google play', 3),
    ],
    'chatbot': [
        ('чат-бот', 5),
        ('чат бот', 5),
        ('бот', 3),
        ('telegram', 3),
        ('whatsapp', 3),
    ],
    'api': [
        ('api', 4),
        ('rest', 4),
        ('graphql', 4),
        ('backend', 3),
        ('бэкенд', 3),
        ('интеграционн', 2),
    ],
    'website': [
        ('лендинг', 5),
        ('сайт-визитк', 5),
        ('корпоративный сайт', 5),
        ('промо-сайт', 4),
    ],
    'web_app': [
        ('веб-сервис', 4),
        ('web-сервис', 4),
        ('веб-прилож', 5),
        ('web app', 5),
        ('dashboard', 3),
        ('дашборд', 3),
        ('личный кабинет', 3),
        ('авторизац', 2),
        ('задач', 2),
        ('админ', 2),
        ('панель', 2),
    ],
}


FEATURE_RULES = [
    ('авторизация', 'medium', ['авторизац', 'логин', 'регистрац']),
    ('управление задачами', 'medium', ['задач', 'task']),
    ('dashboard', 'medium', ['dashboard', 'дашборд', 'панель']),
    ('CRUD-операции', 'medium', ['создание', 'редактирование', 'удаление']),
    ('экспорт данных', 'medium', ['экспорт', 'csv', 'xlsx', 'excel', 'json']),
    ('уведомления', 'medium', ['уведомлен', 'email', 'sms']),
    ('онлайн-оплата', 'critical', ['оплат', 'платеж']),
    ('интеграция с CRM', 'high', ['crm', 'amocrm']),
    ('интеграция с 1С', 'high', ['1с']),
    ('ML/AI-модуль', 'high', ['ai', 'ml', 'нейросет', 'модель', 'прогноз']),
    ('логирование действий', 'low', ['логирован', 'аудит']),
    ('мониторинг и метрики', 'medium', ['мониторинг', 'метрик']),
    ('шифрование данных', 'critical', ['шифрован', 'персональные данные', 'безопасн']),
]


def _score_project_types(text_lower: str) -> dict[str, int]:
    scores = {project_type: 0 for project_type in PROJECT_TYPE_RULES}
    for project_type, rules in PROJECT_TYPE_RULES.items():
        for keyword, weight in rules:
            if keyword in text_lower:
                scores[project_type] += weight
    return scores


def _detect_project_type(text_lower: str) -> str:
    scores = _score_project_types(text_lower)

    # AI should win only when AI-specific wording is explicit enough.
    if scores['ai_service'] < 3:
        scores['ai_service'] = 0

    winner, score = max(scores.items(), key=lambda item: item[1])
    if score == 0:
        return 'web_app'
    return winner


def _detect_features(text_lower: str) -> list[dict[str, str]]:
    features = []
    seen = set()
    for name, complexity, keywords in FEATURE_RULES:
        if name in seen:
            continue
        if any(keyword in text_lower for keyword in keywords):
            features.append({'name': name, 'complexity': complexity})
            seen.add(name)
    return features


def _detect_integrations(text_lower: str) -> list[str]:
    integration_map = {
        'amocrm': ['amocrm', 'amo crm'],
        'crm': ['crm'],
        '1c': ['1с', '1c', 'erp'],
        'payment_gateway': ['оплата', 'платеж', 'эквайринг', 'qr'],
        'telegram': ['telegram', 'телеграм'],
        'whatsapp': ['whatsapp', 'ватсап'],
        'avito': ['avito', 'авито'],
    }
    integrations = []
    for system, keys in integration_map.items():
        if any(key in text_lower for key in keys) and system not in integrations:
            integrations.append(system)
    return integrations


def _detect_platforms(text_lower: str, project_type: str) -> list[str]:
    platforms = []
    if any(keyword in text_lower for keyword in ['web', 'веб', 'сайт', 'dashboard', 'дашборд']):
        platforms.append('web')
    if any(keyword in text_lower for keyword in ['mobile', 'мобильн', 'ios', 'android']):
        platforms.append('mobile')
    if any(keyword in text_lower for keyword in ['telegram', 'телеграм']):
        platforms.append('telegram')
    if any(keyword in text_lower for keyword in ['whatsapp', 'ватсап']):
        platforms.append('whatsapp')
    if any(keyword in text_lower for keyword in ['avito', 'авито']):
        platforms.append('avito')

    if not platforms:
        if project_type == 'mobile_app':
            return ['mobile']
        if project_type == 'chatbot':
            return ['telegram']
        return ['web']
    return platforms


def _detect_complexity(text_lower: str, feature_count: int) -> tuple[str, str, str]:
    design_complexity = 'medium'
    backend_complexity = 'medium'
    frontend_complexity = 'medium'

    high_words = [
        'критичный',
        'сложный',
        'высокая нагрузка',
        'высоконагруж',
        'масштабируем',
        'многокомпонент',
        'реальное время',
        'персональные данные',
    ]
    low_words = ['простой', 'небольшой', 'базовый', 'mvp']

    high_count = sum(1 for word in high_words if word in text_lower)
    low_count = sum(1 for word in low_words if word in text_lower)

    if high_count >= 2 or feature_count >= 8:
        backend_complexity = 'high'
        frontend_complexity = 'high'
    elif low_count >= 1 and feature_count <= 4:
        design_complexity = 'low'
        backend_complexity = 'medium'
        frontend_complexity = 'medium'

    if any(word in text_lower for word in ['уникальный дизайн', 'сложный дизайн', 'анимац']):
        design_complexity = 'high'

    return design_complexity, backend_complexity, frontend_complexity


def _detect_deadline_weeks(text: str) -> int:
    weeks_match = re.search(r'(\d+)\s*(недель|недели|неделю|нед\.|week|weeks)', text, re.IGNORECASE)
    if weeks_match:
        weeks = int(weeks_match.group(1))
        if 1 <= weeks <= 104:
            return weeks
    return 20


def extract_project_data(text: str) -> dict[str, Any]:
    text_clean = text[:1000].strip()
    text_lower = text.lower()
    project_type = _detect_project_type(text_lower)
    features = _detect_features(text_lower)
    design_complexity, backend_complexity, frontend_complexity = _detect_complexity(text_lower, len(features))

    return {
        'project_type': project_type,
        'name': PROJECT_TYPE_NAMES.get(project_type, PROJECT_TYPE_NAMES['other']),
        'description': text_clean,
        'features': features,
        'design_complexity': design_complexity,
        'backend_complexity': backend_complexity,
        'frontend_complexity': frontend_complexity,
        'target_platforms': _detect_platforms(text_lower, project_type),
        'integrations': _detect_integrations(text_lower),
        'deadline_weeks': _detect_deadline_weeks(text),
        'currency': 'RUB',
        'similar_projects_found': 0,
    }
