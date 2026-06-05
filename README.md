# IT Estimator

IT Estimator - сервис для оценки IT-проектов по текстовому описанию или файлу.

Проект состоит из двух частей:

- `backend` - FastAPI API, расчет оценки, хранение проектов, экспорт, интеграция с Ollama.
- `frontend` - Next.js UI для dashboard, проектов, ролей, архива и карточки проекта.
- `postgres` - PostgreSQL база данных с SQL-миграциями.

## Быстрый запуск

Требования:

- Docker
- Docker Compose
- Ollama опционально, если нужен LLM-анализ

Подготовка:

```bash
cp .env.example .env
```

Запуск:

```bash
docker compose up -d --build
```

Адреса:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Backend docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

Остановка:

```bash
docker compose down
```

Логи:

```bash
docker compose logs -f backend
docker compose logs -f frontend
```

## База Данных

Compose поднимает PostgreSQL:

```env
DATABASE_URL=postgresql://estimator:estimator@postgres:5432/estimator
```

Миграции лежат в `backend/app/internal/repository/migrations/` и применяются при старте backend.

Если нужна пара начальных demo-проектов:

```bash
docker compose exec backend python backend/scripts/seed_postgres.py
```

## Ollama

Ollama опциональна. По умолчанию в `.env.example` стоит:

```env
LLM_ENABLED=false
```

В этом режиме backend всё равно:

- анализирует текст или файл;
- считает оценку;
- сохраняет проект в PostgreSQL;
- отдаёт проект во frontend.

Но LLM-блок будет сохранён как fallback:

```text
Не удалось получить ответ от языковой модели.
```

Если нужен локальный LLM-анализ, установи Ollama на хост и скачай модель:

```bash
ollama pull qwen2.5:3b
```

В `.env` включи:

```env
LLM_ENABLED=true
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b
```

В Docker backend обращается к Ollama на хосте через `host.docker.internal:11434`. На Linux может понадобиться разрешить Ollama слушать не только `127.0.0.1`.

Создай systemd override:

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d

sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<'EOF'
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama
```

Проверка на хосте:

```bash
curl http://127.0.0.1:11434/api/tags
ss -ltnp | grep 11434
```

Если включён `ufw`, он может блокировать доступ контейнера к Ollama. Узнай docker subnet:

```bash
docker network inspect estimator_default --format '{{json .IPAM.Config}}'
```

Пример для сети `172.21.0.0/16` и bridge `br-f9b07dd9a141`:

```bash
sudo ufw allow in on br-f9b07dd9a141 from 172.21.0.0/16 to any port 11434 proto tcp
sudo ufw reload
```

Проверка из backend-контейнера:

```bash
docker compose exec backend python -c "import httpx; print(httpx.get('http://host.docker.internal:11434/api/tags', timeout=5).status_code)"
```

Если `host.docker.internal` не проходит, но конкретный gateway работает, укажи его в `.env`. Пример:

```env
OLLAMA_BASE_URL=http://172.21.0.1:11434
```

Если машина слабая или Ollama работает в CPU-only mode, лучше начинать с `qwen2.5:3b`, а не с 7B.

## Основные API

- `GET /projects`
- `GET /projects/archived`
- `GET /projects/{id}`
- `POST /projects/{id}/archive`
- `POST /projects/{id}/restore`
- `DELETE /projects/{id}`
- `GET /projects/{id}/export?format=json|csv|xls|xlsx`
- `GET /roles`
- `GET /settings/rates`
- `PUT /settings/rates`
- `POST /analyze`
- `POST /analyze-file`

## Структура

```text
backend/
  app/
    api/              HTTP handlers and schemas
    core/             settings and env config
    internal/
      domain/         domain models
      repository/     database access
        migrations/   SQL migrations
      service/        business logic
frontend/
  app/                Next.js App Router pages
  components/         UI and layout components
  lib/                API client and shared frontend utilities
```

## Важные файлы

- `.env.example` - пример конфигурации.
- `project_estimator.json` - роли, ставки, уровни и коэффициенты оценки.
- `backend/app/internal/repository/migrations/` - SQL-миграции PostgreSQL.
- `REPOSITORY_AUDIT.md` - заметки по тому, что хранить в репозитории, а что считать локальными/генерируемыми данными.

## Проверка после запуска

```bash
curl http://localhost:8000/projects
curl http://localhost:3000/dashboard
```

## Тесты

Backend:

```bash
docker compose run --rm backend pytest backend/tests
```

Подробный план покрытия: `TESTING.md`.
