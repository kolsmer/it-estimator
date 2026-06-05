from fastapi import APIRouter, File, UploadFile

from backend.app.api.schemas.analysis import ProjectInput
from backend.app.core.config import ESTIMATOR_CONFIG_PATH
from backend.app.internal.repository.project_storage import save_to_db
from backend.app.internal.service.estimation_service import EstimationFacade
from backend.app.internal.service.file_text_extractor import extract_text_from_bytes
from backend.app.internal.service.llm_service import create_prompt, get_llm_response
from backend.app.internal.service.project_parser import extract_project_data


router = APIRouter()


def _run_analysis(text: str) -> dict:
    project_data = extract_project_data(text)

    facade = EstimationFacade(str(ESTIMATOR_CONFIG_PATH))
    result = facade.estimate_from_ai_input(project_data)
    if not result.get('success'):
        return {'success': False, 'error': result.get('error', 'Ошибка расчёта')}

    estimate = result['data']
    prompt = create_prompt(project_data, estimate)
    llm_response = get_llm_response(prompt)
    if not llm_response:
        llm_response = 'Не удалось получить ответ от языковой модели.'

    save_to_db(project_data, estimate, llm_response)
    return {'success': True, 'project_data': project_data, 'estimate': estimate, 'llm': llm_response}


@router.post('/analyze')
def analyze_project(data: ProjectInput):
    try:
        return _run_analysis(data.text)
    except Exception as e:
        return {'success': False, 'error': str(e)}


@router.post('/analyze-file')
async def analyze_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        text = extract_text_from_bytes(file.filename, content)
        return _run_analysis(text)
    except Exception as e:
        return {'success': False, 'error': str(e)}
