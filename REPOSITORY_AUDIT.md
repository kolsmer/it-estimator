# Repository Audit

Цель документа - отделить исходный код и нужные примеры от локальных данных, временных файлов и сгенерированных артефактов.

## Хранить в репозитории

- `backend/` - backend-код FastAPI.
- `frontend/` - frontend-код Next.js.
- `docker-compose.yml` - локальный запуск backend + frontend.
- `backend/Dockerfile` - сборка backend.
- `.env.example` - пример переменных окружения.
- `project_estimator.json` - рабочая конфигурация оценщика: роли, ставки, уровни, коэффициенты.
- `README.md` - инструкция запуска.
- `my_it_project/PROJECT_OVERVIEW.md` - проектная документация.

## Не хранить в репозитории

- `.env` - локальные секреты и настройки окружения.
- `.venv/` - локальное Python-окружение.
- `frontend/node_modules/` - зависимости Node.js.
- `frontend/.next/` - кеш и сборка Next.js.
- `example.db` - старая локальная SQLite база с runtime-данными после перехода на PostgreSQL.
- `report_with_llm.json` - сгенерированный отчет.
- `project_estimate.json` - сгенерированный результат оценки.
- `projects_history.json` - локальная история frontend/runtime.
- `backend/scripts/test_export/` - тестовые выгрузки.
- `project_facture/facture_report.json` - сгенерированный отчет.
- `project_facture/facture_summary.txt` - сгенерированная сводка.
- `project_facture/project_facture` - локальный артефакт.
- `.idea/`, `.vscode/` - локальные настройки IDE.
- `test-main/` - старая frontend-папка после переноса в `frontend/`.

## Проверить вручную перед удалением

- `config.json` - выглядит как дубль `project_estimator.json`; лучше оставить только один источник правды.
- `project_description.txt` - может быть примером входного описания, но сейчас лежит как обычный файл в корне.
- `project_facture/*.docx` - тестовые/примерные документы; можно перенести в `docs/examples/` или `backend/scripts/test_files/`.
- `my_it_project/*.docx` - документы для понимания проекта; если нужны стажеру, лучше хранить в `docs/`.
- `projects/proekti` - неочевидный файл без расширения; нужно решить, это пример входных данных или локальный мусор.
- `backend/scripts/make_pdf_test.py`, `export_projects.py`, `update_rates_test.py` - полезны как dev-скрипты, но лучше переименовать/разнести по `scripts/dev/` или заменить тестами.

## Эксплуатационная готовность

- Docker Compose есть и запускает backend + frontend + PostgreSQL.
- `.env.example` есть.
- Корневой `README.md` добавлен.
- `.gitlab-ci.yml` сейчас отсутствует, CI не настроен.
- Для production лучше добавить миграции БД, тесты и отдельный compose/profile для Ollama.

## Вывод

Проект уже можно запускать локально, но репозиторий пока содержит смесь исходников, локальных данных и примеров. Главный следующий шаг - принять решение по примерным документам и удалить из git runtime-файлы, если они уже были закоммичены.
