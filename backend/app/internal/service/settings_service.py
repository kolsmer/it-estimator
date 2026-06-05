from __future__ import annotations

import json

from fastapi import HTTPException

from backend.app.core.config import ESTIMATOR_CONFIG_PATH
from backend.app.api.schemas.settings import RateUpdateInput


def load_estimator_config() -> dict:
    with open(ESTIMATOR_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_estimator_config(config_data: dict) -> None:
    with open(ESTIMATOR_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)


def get_rates() -> dict:
    config_data = load_estimator_config()
    return {
        'currency': config_data.get('metadata', {}).get('currency', 'RUB'),
        'rates': config_data.get('rate_card_rub', {}),
    }


def update_rate(payload: RateUpdateInput) -> dict:
    if payload.rate <= 0:
        raise HTTPException(status_code=400, detail='Rate must be greater than zero')

    config_data = load_estimator_config()
    rate_card = config_data.setdefault('rate_card_rub', {})
    role_rates = rate_card.get(payload.role)
    if role_rates is None:
        raise HTTPException(status_code=404, detail='Role not found')
    if payload.seniority not in role_rates:
        raise HTTPException(status_code=404, detail='Seniority not found')

    role_rates[payload.seniority] = payload.rate
    save_estimator_config(config_data)

    return {
        'success': True,
        'message': 'Ставка обновлена',
        'role': payload.role,
        'seniority': payload.seniority,
        'rate': payload.rate,
    }


def list_roles() -> list[dict]:
    config_data = load_estimator_config()
    roles = config_data.get('roles', {})
    rate_card = config_data.get('rate_card_rub', {})
    currency = config_data.get('metadata', {}).get('currency', 'RUB')

    result = []
    for role_key, role_info in roles.items():
        role_rates = rate_card.get(role_key, {})
        for seniority, rate in role_rates.items():
            result.append(
                {
                    'id': f'{role_key}:{seniority}',
                    'role': f"{role_info.get('name', role_key)} ({seniority})",
                    'rate': float(rate),
                    'currency': currency,
                    'role_key': role_key,
                    'seniority': seniority,
                }
            )
    return result
