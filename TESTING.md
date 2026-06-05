# Testing Plan

## Что уже добавлено

Минимальные backend-тесты лежат в `backend/tests/`.

Они проверяют:

- список активных проектов;
- список архивных проектов через `GET /projects/archived`;
- карточку проекта и `404`, если проект не найден;
- экспорт проекта в `json`;
- ошибку при неподдерживаемом формате экспорта;
- архивирование, восстановление и удаление проекта;
- запуск `/analyze` без реальной БД и без реальной Ollama;
- получение и обновление ставок;
- базовое извлечение features из текстового описания.

Запуск:

```bash
pytest backend/tests
```

В Docker:

```bash
docker compose exec backend pytest backend/tests
```

## Что покрыть следующим

- Repository-тесты на PostgreSQL test database: `save_to_db`, `list_active_projects`, `archive_project`, `restore_project`, `delete_project`.
- Seed-сценарий начальных PostgreSQL данных: `backend/scripts/seed_postgres.py`.
- Экспорт `csv`, `xls`, `xlsx` с проверкой content-type и читаемости файла.
- `/analyze-file` для `txt`, `json`, `csv`, `docx`, `pdf`.
- Ошибки загрузки файлов: пустой файл, неизвестное расширение, битый `pdf/docx`.
- Настройки ставок: несуществующая роль, несуществующий seniority, отрицательная ставка.
- LLM fallback: Ollama выключена, Ollama недоступна, модель вернула пустой ответ.
- Frontend integration/e2e: dashboard, projects, details, archive, roles against real backend.

## Критичные сценарии без полноценной защиты

- Потеря проекта при archive/restore/delete.
- Расхождение структуры ответа backend и типов frontend. Например, backend в `GET /projects/{id}` перестанет отдавать `cost`, `hours`, `status` или `llm_analysis`, либо переименует `cost` в `total_cost_rub`; frontend при этом ожидает старые поля в `frontend/lib/backend.ts` и начнет показывать `0 ₽`, пустой LLM-блок или сломанную карточку проекта.
- Поломка parser -> estimator pipeline после изменения `project_estimator.json`.
- Обрезанный или пустой LLM-анализ.
- Повреждение `project_estimator.json` после обновления ставок.
- Накопление runtime-файлов в git: `.db`, `.next`, `node_modules`, generated reports.
