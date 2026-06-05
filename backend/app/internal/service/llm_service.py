from __future__ import annotations

import json
import threading
import traceback
from datetime import datetime

import httpx
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from backend.app.core.config import (
    LLM_ENABLED,
    OLLAMA_BASE_URL,
    OLLAMA_KEEP_ALIVE,
    OLLAMA_MODEL,
    OLLAMA_HEALTH_TIMEOUT_SECONDS,
    OLLAMA_NUM_CTX,
    OLLAMA_NUM_PREDICT,
    OLLAMA_NUM_THREAD,
    OLLAMA_TIMEOUT_SECONDS,
)

_LLM_LOCK = threading.Lock()


def create_prompt(project_data: dict, estimate: dict) -> str:
    features = project_data.get("features") or []
    features_list = "\n".join([f"- {f['name']} ({f['complexity']})" for f in features]) or "- не выделены"

    return f"""
Вы — эксперт по оценке IT-проектов. Напишите короткое пояснение к уже готовой оценке.
Не пересчитывайте оценку и не меняйте числа.
Используйте только факты из блока ДАННЫЕ.

ДАННЫЕ:
- Название: {project_data['name']}
- Тип: {project_data['project_type']}
- Описание: {project_data['description']}
- Функции:
{features_list}
- Стоимость: {estimate['total_cost_rub']:,.0f} ₽
- Часы: {estimate['total_hours']} ч
- Длительность: {estimate['duration_weeks']} недель
- Команда: {estimate['team_size']} человек
- Уверенность оценки: {estimate['confidence_score']:.0%}

Сформируйте короткий управленческий вывод строго в таком формате:

Суть:
- одно предложение о цели проекта
- одно предложение о сроках и масштабе

Риски:
- риск 1
- риск 2
- риск 3

Рекомендации:
- рекомендация 1
- рекомендация 2
- рекомендация 3

Итог:
- одно короткое финальное предложение

Правила:
- не используйте вложенную нумерацию;
- не начинайте пункты с "1.", "2.", "3.";
- не пишите вступление;
- не больше 100 слов;
- длительность должна быть ровно {estimate['duration_weeks']} недель;
- команда должна быть ровно {estimate['team_size']} человек;
- если данных мало, не придумывайте лишние детали.
"""


def get_llm_response(prompt: str) -> str | None:
    if not LLM_ENABLED:
        print("LLM disabled: set LLM_ENABLED=true to enable Ollama analysis")
        return None

    try:
        httpx.get(f'{OLLAMA_BASE_URL.rstrip("/")}/api/tags', timeout=OLLAMA_HEALTH_TIMEOUT_SECONDS)

        # CPU-only Ollama is easy to overload with parallel requests.
        with _LLM_LOCK:
            llm = OllamaLLM(
                model=OLLAMA_MODEL,
                base_url=OLLAMA_BASE_URL,
                temperature=0.1,
                num_ctx=OLLAMA_NUM_CTX,
                num_thread=OLLAMA_NUM_THREAD,
                num_predict=OLLAMA_NUM_PREDICT,
                keep_alive=OLLAMA_KEEP_ALIVE,
                sync_client_kwargs={'timeout': OLLAMA_TIMEOUT_SECONDS},
            )
            chain = ChatPromptTemplate.from_template("{input}") | llm
            response = chain.invoke({"input": prompt})
            return str(response).strip()
    except httpx.TimeoutException:
        print(f"LLM unavailable: Ollama timed out at {OLLAMA_BASE_URL}")
        return None
    except httpx.RequestError as e:
        print(f"LLM unavailable: cannot connect to Ollama at {OLLAMA_BASE_URL}: {e}")
        return None
    except Exception as e:
        print(f"❌ Ошибка при вызове LLM: {e}")
        traceback.print_exc()
        return None


def save_report(project_data: dict, estimate: dict, llm_response: str) -> None:
    report = {
        "input_project": project_data,
        "estimation": estimate,
        "llm_analysis": llm_response,
        "generated_at": datetime.now().isoformat(),
    }
    try:
        with open("report_with_llm.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print("✅ Отчёт сохранён: report_with_llm.json")
    except IOError as e:
        print(f"❌ Ошибка при сохранении отчёта: {e}")
        traceback.print_exc()
