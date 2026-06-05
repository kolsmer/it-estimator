import json
import os
from decimal import Decimal


class ConfigLoader:
    def __init__(self, config_path: str = "project_estimator.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            self.config_path = os.path.join(os.path.dirname(__file__), "project_estimator.json")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл {self.config_path} не найден.")

    @property
    def currency(self) -> str:
        return self.config['metadata'].get('currency', 'RUB')

    def get_project_type_base_hours(self, project_type: str) -> int:
        return self.config['project_types'].get(project_type, {}).get('base_hours', 200)

    def get_project_type_name(self, project_type: str) -> str:
        return self.config['project_types'].get(project_type, {}).get('name', project_type)

    def get_role_name(self, role: str) -> str:
        return self.config['roles'].get(role, {}).get('name', role)

    def get_seniority_name(self, seniority: str) -> str:
        return self.config['seniority_levels'].get(seniority, {}).get('name', seniority)

    def get_complexity_multiplier(self, complexity: str) -> float:
        return self.config['complexity_levels'].get(complexity, {}).get('multiplier', 1.0)

    def get_rate_rub(self, role: str, seniority: str) -> Decimal:
        rate_card = self.config['rate_card_rub']
        role_rates = rate_card.get(role, {})
        rate = role_rates.get(seniority)

        if rate is None:
            if seniority in ['junior', 'middle'] and role == 'architect':
                rate = role_rates.get('senior', 8100)
            else:
                rate = role_rates.get('middle', 3600)

        return Decimal(str(rate))

    def get_role_distribution(self, project_type: str) -> dict[str, float]:
        return self.config['role_distribution'].get(
            project_type,
            self.config['role_distribution']['other'],
        )

    def get_seniority_distribution(self, complexity: str) -> dict[str, float]:
        return self.config['seniority_distribution'].get(
            complexity,
            self.config['seniority_distribution']['medium'],
        )

    def get_project_stages(self) -> dict[str, dict]:
        return self.config['project_stages']

    def get_confidence_factors(self) -> dict:
        return self.config['confidence_factors']

    def get_calculation_rules(self) -> dict:
        return self.config['calculation_rules']
