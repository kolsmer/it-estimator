import json
import os
import traceback

from backend.app.core.config import ESTIMATOR_CONFIG_PATH
from backend.app.internal.repository.project_storage import init_db, save_to_db, show_all_project
from backend.app.internal.service.estimation_service import EstimationFacade
from backend.app.internal.service.llm_service import create_prompt, get_llm_response, save_report
from backend.app.internal.service.project_parser import extract_project_data


def main() -> None:
    try:
        init_db()
        show_all_project()

        if not os.path.exists('project_description.txt'):
            print('❌ Файл project_description.txt не найден!')
            return

        with open('project_description.txt', 'r', encoding='utf-8') as f:
            text = f.read()

        project_data = extract_project_data(text)
        print('✅ Данные извлечены:', json.dumps(project_data, indent=2, ensure_ascii=False))

        facade = EstimationFacade(str(ESTIMATOR_CONFIG_PATH))
        result = facade.estimate_from_ai_input(project_data)
        if not result['success']:
            print('❌ Ошибка расчёта:', result['error'])
            return

        estimate = result['data']
        print('✅ Расчёт готов')

        prompt = create_prompt(project_data, estimate)
        llm_response = get_llm_response(prompt)
        if llm_response:
            print('✅ Ответ LLM получен')
        else:
            print('⚠️ Ответ LLM пустой или не получен')
            llm_response = 'Не удалось получить ответ от языковой модели.'

        save_report(project_data, estimate, llm_response)
        save_to_db(project_data, estimate, llm_response)

        print('\n' + '=' * 60)
        print('ИТОГ: КРАТКИЙ ОБЗОР')
        print('=' * 60)
        print(f"Проект: {estimate['project_name']}")
        print(f"Тип: {estimate['project_type']}")
        print(f"Общая стоимость: {estimate['total_cost_rub']:,.2f} ₽")
        print(f"Общее количество часов: {estimate['total_hours']}")
        print(f"Длительность: {estimate['duration_weeks']} недель")
        print(f"Размер команды: {estimate['team_size']} человек")
        print(f"Средняя ставка: {estimate['hourly_rate_avg_rub']:,.0f} ₽/час")
        print(f"Достоверность оценки: {estimate['confidence_score']:.0%}")

        print('\n--- РАСПРЕДЕЛЕНИЕ ПО РОЛЯМ ---')
        for role in estimate['roles']:
            print(
                f"{role['role_name']} ({role['seniority_name']}): "
                f"{role['total_hours']} часов, {role['count']} чел., {role['cost_rub']:,.0f} ₽"
            )

        print('\n--- ЭТАПЫ ПРОЕКТА ---')
        for stage_name, stage in estimate['stages'].items():
            print(f"{stage_name}: {stage['cost_rub']:,.0f} ₽ ({stage['duration_weeks']} нед.)")

        print('\n🔍 Анализ LLM:')
        print('-' * 60)
        print(llm_response)

    except Exception as e:
        print(f'❌ Произошла ошибка: {e}')
        traceback.print_exc()


if __name__ == '__main__':
    main()
