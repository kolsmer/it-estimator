#!/usr/bin/env python3
import json
from pathlib import Path
import copy
import sys

# ensure project root is on sys.path so imports work from scripts/ folder
BASE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE))

from backend.app.internal.service.estimation_service import EstimationFacade

CONFIG_PATH = BASE / 'project_estimator.json'


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_estimate(config, ai_input):
    # write temp config
    tmp = BASE / 'tmp_project_estimator.json'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    facade = EstimationFacade(str(tmp))
    res = facade.estimate_from_ai_input(ai_input)
    tmp.unlink()
    return res


def main():
    cfg = load_config(CONFIG_PATH)
    # simple AI input example
    ai_input = {
        'project_type': 'ai_service',
        'name': 'AI project',
        'description': 'test',
        'features': [],
        'design_complexity': 'medium',
        'backend_complexity': 'medium',
        'frontend_complexity': 'medium',
        'deadline_weeks': 12,
        'currency': 'RUB'
    }

    before = run_estimate(cfg, ai_input)
    print('Before total_cost:', before['data']['total_cost_rub'])

    # modify one rate (e.g., backend_developer middle)
    cfg2 = copy.deepcopy(cfg)
    try:
        cfg2['rate_card_rub']['backend_developer']['middle'] = cfg2['rate_card_rub']['backend_developer']['middle'] * 1.5
    except Exception as e:
        print('Failed to modify config:', e)
        return
    after = run_estimate(cfg2, ai_input)
    print('After total_cost:', after['data']['total_cost_rub'])


if __name__ == '__main__':
    main()
