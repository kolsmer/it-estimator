# Check Report

Дата отчета: 2026-06-04

## Краткий вывод

Проект сейчас находится в рабочем MVP-состоянии: backend, frontend, PostgreSQL, базовые API, анализ проекта, экспорт, архивирование, восстановление, удаление, ставки и интеграция с Ollama уже собраны в одну локальную систему через Docker Compose.

Главный риск сейчас не в том, что система не запускается, а в том, что часть решений еще хрупкая: мало тестов, есть технический долг после переноса файлов, LLM зависит от локальной настройки Ollama на машине разработчика, а Next.js dev-cache ранее ломался из-за смешивания dev/prod-сборок в одной папке.

## Что работает

- Backend на FastAPI запускается через Docker Compose.
- PostgreSQL (перешли с sqlite на postgresql) поднимается отдельным сервисом в Docker Compose.
- SQL-миграции применяются при старте backend.
- API проектов работает:
  - `GET /projects`
  - `GET /projects/archived`
  - `GET /projects/{id}`
  - `POST /projects/{id}/archive`
  - `POST /projects/{id}/restore`
  - `DELETE /projects/{id}`
  - `GET /projects/{id}/export`
- API анализа работает:
  - `POST /analyze`
  - `POST /analyze-file`
- Экспорт поддерживает `json`, `csv`, `xls`, `xlsx`.
- API ставок работает:
  - `GET /settings/rates`
  - `PUT /settings/rates`
- Frontend на Next.js запускается через Docker Compose.
- Страницы frontend работают:
  - dashboard
  - projects
  - project details
  - roles
  - archive
- Frontend обращается к реальному backend API, старый mock-режим убран.
- Dashboard показывает проекты из backend.
- Страница проекта показывает LLM-анализ, требования, расчет, экспорт и действия управления.
- Ollama подключается к backend из Docker-контейнера при корректной настройке `OLLAMA_BASE_URL`, systemd override и firewall.
- При `LLM_ENABLED=false` система продолжает работать без Ollama: проект анализируется, считается и сохраняется, но LLM-блок заполняется fallback-текстом.
- Добавлено минимальное backend-тестовое покрытие.
- Добавлены документы:
  - `README.md`
  - `TESTING.md`
  - `REPOSITORY_AUDIT.md`

## Что не работает или остается хрупким

- Ollama не является полностью переносимой частью Docker Compose: она запускается на хосте, поэтому каждому разработчику нужно отдельно настроить Ollama и доступ контейнера к `11434`.
- На Linux с активным `ufw` доступ backend-контейнера к Ollama может блокироваться firewall.
- CPU-only Ollama работает медленно на больших описаниях проекта, поэтому анализ файла может занимать десятки секунд.
- Если использовать большую модель, например 7B, слабая машина может зависать или крашиться.
- Next.js cache ранее ломался из-за того, что dev-сервер и production build писали в одну папку `.next`.
- В `docker-compose.yml` frontend все еще использует bind mount `./frontend:/app`, поэтому generated-файлы frontend зависят от поведения контейнера.
- Есть предупреждение FastAPI по `@app.on_event('startup')`: желательно перейти на lifespan API.
- Тесты пока минимальные и в основном проверяют API через monkeypatch, а не полноценную связку с реальной PostgreSQL test database.
- Нет CI/CD: `.gitlab-ci.yml` отсутствует.
- Нет production-ready стратегии деплоя, мониторинга, бэкапов и secrets management.


## Архитектурные проблемы

- Backend все еще частично несет следы MVP-структуры и переноса файлов.
- LLM-интеграция завязана на локальную инфраструктуру разработчика.
- Нет явного контрактного тестирования между схемой ответа backend и frontend TypeScript-типами.
- Нет полноценной доменной модели для "качества оценки", "типа проекта", "клиента", "feature extraction" и LLM-анализа.

## Что было исправлено

- Backend и frontend разнесены по отдельным папкам:
  - `backend/`
  - `frontend/`
- Старый mock-режим frontend убран.
- Docker Compose приведен к основным сервисам:
  - `postgres`
  - `backend`
  - `frontend`
- Добавлен PostgreSQL вместо старого runtime-подхода с SQLite.
- Добавлены SQL-миграции для базы.
- Добавлен скрипт для начальных demo-данных в бд.
- Backend API прокинут во frontend через реальный `NEXT_PUBLIC_BACKEND_URL`.
- Добавлены необходимые эндпойнты и дополнительно `GET /projects/archived` для страницы архива.
- Улучшен prompt для LLM-анализа.
- Добавлены настройки Ollama через `.env`:
  - `LLM_ENABLED`
  - `OLLAMA_BASE_URL`
  - `OLLAMA_MODEL`
  - `OLLAMA_NUM_CTX`
  - `OLLAMA_NUM_THREAD`
  - `OLLAMA_NUM_PREDICT`
  - `OLLAMA_TIMEOUT_SECONDS`
  - `OLLAMA_KEEP_ALIVE`
- Добавлен health-check Ollama перед генерацией.
- Добавлен lock для LLM-запросов, чтобы CPU-only Ollama не перегружалась параллельными запросами.
- Добавлен fallback при отключенной или недоступной Ollama.
- Для frontend добавлен безопасный скрипт `build:check`, чтобы production build не ломал dev-cache `.next`.
- Добавлен `.gitignore`
- Добавлены минимальные backend-тесты.
- Добавлена документация по запуску, тестам, Ollama и состоянию репозитория.

## Что остается сделать

### Критично

- Убрать неоднозначность поля `client`: либо реально извлекать клиента из входных данных, либо полностью заменить это поле на `project_type`.
- Добавить контрактные тесты между backend и frontend, чтобы frontend не ломался при изменении структуры ответа API.
- Добавить repository/integration tests на PostgreSQL test database.
- Стабилизировать Next.js cache в Docker: лучше вынести `.next` в Docker volume или полностью отделить dev-cache от host bind mount.
- Добавить CI, который запускает backend-тесты и frontend build check.

### Важно

- Перейти с FastAPI `@app.on_event('startup')` на lifespan.
- Добавить полноценную валидацию входных данных для `/analyze` и `/analyze-file`.
- Добавить тесты экспорта `csv`, `xls`, `xlsx`.
- Добавить тесты для ошибок файлов: пустой файл, битый файл, неизвестный формат.
- Добавить тесты LLM fallback:
  - `LLM_ENABLED=false`
  - Ollama недоступна
  - модель вернула пустой ответ
  - timeout генерации
- Отдельный compose для Ollama, если понадобится
- Улучшить парсер фичей, чтобы оценка меньше зависела от простых эвристик.
- Добавить обработку ошибок PostgreSQL и более явные HTTP-ответы.

