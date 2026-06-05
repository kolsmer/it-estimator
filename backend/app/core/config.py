from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parents[2]
load_dotenv(PROJECT_ROOT / '.env')


def _env_path(name: str, default: Path) -> Path:
    value = os.getenv(name)
    if not value:
        return default
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _env_csv(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://estimator:estimator@localhost:5432/estimator')
ESTIMATOR_CONFIG_PATH = _env_path('ESTIMATOR_CONFIG_PATH', PROJECT_ROOT / 'project_estimator.json')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')
LLM_ENABLED = _env_bool('LLM_ENABLED', False)
OLLAMA_NUM_CTX = _env_int('OLLAMA_NUM_CTX', 1024)
OLLAMA_NUM_THREAD = _env_int('OLLAMA_NUM_THREAD', 2)
OLLAMA_NUM_PREDICT = _env_int('OLLAMA_NUM_PREDICT', 256)
OLLAMA_HEALTH_TIMEOUT_SECONDS = _env_int('OLLAMA_HEALTH_TIMEOUT_SECONDS', 5)
OLLAMA_TIMEOUT_SECONDS = _env_int('OLLAMA_TIMEOUT_SECONDS', 180)
OLLAMA_KEEP_ALIVE = os.getenv('OLLAMA_KEEP_ALIVE', '0s')
ALLOWED_ORIGINS = _env_csv('ALLOWED_ORIGINS', '*')
