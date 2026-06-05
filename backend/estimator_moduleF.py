import json

from backend.app.internal.domain.enums import ComplexityLevel, ProjectType, RoleType, SeniorityLevel
from backend.app.internal.domain.models import Feature, ProjectEstimate, ProjectInput, ProjectStage, RoleAssignment
from backend.app.internal.service.estimator_config import ConfigLoader
from backend.app.internal.service.estimation_service import EstimationFacade, ProjectEstimator, process_data


def example_usage():
    facade = EstimationFacade("project_estimator.json")

    ai_input = {
        "project_type": "ecommerce",
        "name": "Маркетплейс для фермерских продуктов",
        "description": "Платформа где фермеры могут продавать продукты напрямую покупателям",
        "design_complexity": "medium",
        "backend_complexity": "high",
        "frontend_complexity": "medium",
        "features": [
            {"name": "Аутентификация и профили", "complexity": "medium"},
            {"name": "Каталог товаров с фильтрацией", "complexity": "high"},
            {"name": "Корзина и оформление заказа", "complexity": "high"},
            {"name": "Интеграция с платежными системами", "complexity": "critical"},
            {"name": "Личный кабинет продавца", "complexity": "high"},
            {"name": "Система рейтингов и отзывов", "complexity": "medium"},
            {"name": "Админ-панель", "complexity": "medium"},
            {"name": "Мобильная адаптация", "complexity": "medium"},
        ],
        "target_platforms": ["web", "mobile"],
        "integrations": ["payment_gateways", "crm", "email_service"],
        "deadline_weeks": 16,
        "currency": "RUB",
        "similar_projects_found": 5,
    }

    result = facade.estimate_from_ai_input(ai_input)

    if result["success"]:
        estimate = result["data"]
        print("=" * 70)
        print("РЕЗУЛЬТАТ РАСЧЁТА ПРОЕКТА")
        print("=" * 70)
        print(f"Проект: {estimate['project_name']}")
        print(f"Тип: {estimate['project_type']}")
        print(f"Общая стоимость: {estimate['total_cost_rub']:,.2f} ₽")
        print(f"Общее количество часов: {estimate['total_hours']}")
        print(f"Длительность: {estimate['duration_weeks']} недель")
        print(f"Размер команды: {estimate['team_size']} человек")
        print(f"Средняя ставка: {estimate['hourly_rate_avg_rub']:.0f} ₽/час")
        print(f"Достоверность оценки: {estimate['confidence_score'] * 100:.0f}%")

        print("\n--- РАСПРЕДЕЛЕНИЕ ПО РОЛЯМ ---")
        for role in estimate['roles']:
            print(
                f"{role['role_name']} ({role['seniority_name']}): "
                f"{role['total_hours']} часов, {role['count']} чел., "
                f"{role['cost_rub']:,.0f} ₽"
            )

        print("\n--- ЭТАПЫ ПРОЕКТА ---")
        for stage, data in estimate['stages'].items():
            print(f"{data['name']}: {data['cost_rub']:,.0f} ₽ ({data['duration_weeks']} нед.)")

        with open('../project_estimate.json', 'w', encoding='utf-8') as f:
            json.dump(estimate, f, ensure_ascii=False, indent=2)

        print("\n✅ Детальный расчёт сохранён в project_estimate.json")
    else:
        print(f"❌ Ошибка: {result['error']}")


if __name__ == "__main__":
    example_usage()
