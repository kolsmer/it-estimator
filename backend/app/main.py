from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.handlers.analysis import router as analysis_router
from backend.app.api.handlers.projects import router as projects_router
from backend.app.api.handlers.settings import router as settings_router
from backend.app.core.config import ALLOWED_ORIGINS
from backend.app.internal.repository.migrations import run_migrations


app = FastAPI()


@app.on_event('startup')
def startup() -> None:
    run_migrations()


app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
def root():
    return {'message': 'FastAPI работает'}


app.include_router(projects_router)
app.include_router(settings_router)
app.include_router(analysis_router)
