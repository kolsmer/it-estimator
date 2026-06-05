import json
import requests
import re
from typing import Dict, Optional, List, Any
from datetime import datetime


class LocalAIAgent:
    """
    AI-агент для работы с локальной нейросетью Ollama
    Интеграция с вашим расчётным модулем
    """

    def __init__(self, model_name: str = "qwen2.5:3b", host: str = "http://localhost:11434"):
        self.model_name = model_name
        self.host = host
        self.base_url = f"{host}/api/generate"
        self.chat_url = f"{host}/api/chat"

    def is_available(self) -> bool:
        """Проверка доступности нейросети"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def list_models(self) -> List[str]:
        """Получение списка доступных моделей"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
        except:
            pass
        return []

    def analyze_project(self, description: str) -> Dict:
        """
        Анализ текстового описания проекта и извлечение структурированных данных
        Возвращает данные в формате, совместимом с вашим ProjectInput
        """

        # Системный промпт для обучения модели
        system_prompt = """Ты - опытный эксперт по оценке IT-проектов. 
Твоя задача - проанализировать описание проекта и извлечь из него структурированные данные.
Отвечай ТОЛЬКО в формате JSON, без пояснений и лишнего текста.

ВАЖНО: Сложность может быть только: low, medium, high, critical
Тип проекта может быть только: website, web_app, mobile_app, ecommerce, marketplace, crm, erp, api, chatbot, ai_service, other
"""

        # Промпт с инструкциями
        prompt = f"""Проанализируй описание проекта и верни JSON с данными.

Описание проекта:
{description}

На основе описания определи:
1. Тип проекта (выбери строго из: website, web_app, mobile_app, ecommerce, marketplace, crm, erp, api, chatbot, ai_service, other)
2. Придумай короткое название для проекта
3. Сложность дизайна (только: low, medium, high, critical)
4. Сложность бэкенда (только: low, medium, high, critical)
5. Сложность фронтенда (только: low, medium, high, critical)
6. Список ключевых функций (минимум 3, максимум 10) с указанием сложности каждой
7. Целевые платформы (массив из: web, mobile, desktop, tablet)
8. Необходимые интеграции (например: payment, crm, email, sms, analytics)
9. Примерный срок в неделях (если можно определить, иначе null)
10. Количество похожих проектов, которые ты видел (оцени от 0 до 10)

Верни JSON строго в таком формате (без комментариев):
{{
    "project_type": "тип_проекта",
    "name": "название проекта",
    "description": "краткое описание проекта",
    "design_complexity": "сложность",
    "backend_complexity": "сложность",
    "frontend_complexity": "сложность",
    "features": [
        {{"name": "название фичи", "complexity": "сложность", "description": "описание"}}
    ],
    "target_platforms": ["платформа1", "платформа2"],
    "integrations": ["интеграция1", "интеграция2"],
    "deadline_weeks": число,
    "similar_projects_found": число
}}
"""

        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,  # Низкая температура для более точных ответов
                        "num_predict": 2000
                    }
                },
                timeout=60
            )

            response.raise_for_status()
            result = response.json()
            answer = result.get("response", "")

            # Извлекаем JSON из ответа
            json_data = self._extract_json(answer)
            if json_data:
                # Добавляем валюту по умолчанию
                json_data["currency"] = "RUB"

                # Проверяем обязательные поля
                required_fields = ["project_type", "name", "description",
                                   "design_complexity", "backend_complexity",
                                   "frontend_complexity", "features"]

                missing_fields = [f for f in required_fields if f not in json_data]
                if missing_fields:
                    return {
                        "success": False,
                        "error": f"Отсутствуют поля: {missing_fields}",
                        "data": json_data
                    }

                return {
                    "success": True,
                    "data": json_data,
                    "message": "Проект успешно проанализирован"
                }
            else:
                return {
                    "success": False,
                    "error": "Не удалось извлечь JSON из ответа",
                    "raw_response": answer[:500]  # Первые 500 символов для отладки
                }

        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Не удалось подключиться к Ollama",
                "message": "Запустите сервер: ollama serve"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка при обращении к нейросети"
            }

    def enhance_estimate(self, estimate_data: Dict, project_description: str) -> Dict:
        """
        Улучшение оценки с помощью AI (анализ рисков и рекомендации)
        """
        prompt = f"""
        Проанализируй оценку проекта и дай рекомендации.

        Описание проекта: {project_description}

        Оценка:
        - Общая стоимость: {estimate_data.get('total_cost_rub')} ₽
        - Длительность: {estimate_data.get('duration_weeks')} недель
        - Размер команды: {estimate_data.get('team_size')} человек

        Верни JSON с анализом:
        {{
            "risks": ["риск1", "риск2", "риск3"],
            "recommendations": ["рекомендация1", "рекомендация2"],
            "optimization_suggestions": ["идея1", "идея2"],
            "key_factors": ["фактор1", "фактор2"]
        }}
        """

        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3}
                },
                timeout=30
            )

            result = response.json()
            answer = result.get("response", "")

            json_data = self._extract_json(answer)
            if json_data:
                return json_data
            else:
                return {
                    "risks": ["Не удалось проанализировать риски"],
                    "recommendations": ["Проверьте введённые данные"],
                    "optimization_suggestions": [],
                    "key_factors": []
                }

        except Exception:
            return {
                "risks": ["Ошибка при анализе"],
                "recommendations": [],
                "optimization_suggestions": [],
                "key_factors": []
            }

    def _extract_json(self, text: str) -> Optional[Dict]:
        """Извлечение JSON из текста"""
        # Ищем JSON в фигурных скобках
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass

        # Пробуем распарсить весь текст
        try:
            return json.loads(text)
        except:
            return None

    def chat_about_project(self, project_data: Dict, question: str) -> str:
        """
        Чат с AI о конкретном проекте
        """
        context = f"""
        Проект: {project_data.get('project_name')}
        Тип: {project_data.get('project_type')}
        Стоимость: {project_data.get('total_cost_rub')} ₽
        Длительность: {project_data.get('duration_weeks')} недель
        Команда: {project_data.get('team_size')} человек

        Роли в команде:
        {json.dumps(project_data.get('roles', []), indent=2, ensure_ascii=False)}
        """

        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": f"Информация о проекте:\n{context}"},
            {"role": "user", "content": question}
        ]

        try:
            response = requests.post(
                self.chat_url,
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=30
            )

            result = response.json()
            return result.get("message", {}).get("content", "Нет ответа")

        except Exception as e:
            return f"Ошибка: {e}"
