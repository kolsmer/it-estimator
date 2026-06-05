from fastapi import APIRouter

from backend.app.api.schemas.settings import RateUpdateInput
from backend.app.internal.service.settings_service import (
    get_rates as get_rates_data,
    list_roles,
    update_rate as update_rate_data,
)


router = APIRouter()


@router.get('/settings/rates')
def get_rates():
    return get_rates_data()


@router.put('/settings/rates')
def update_rate(payload: RateUpdateInput):
    return update_rate_data(payload)


@router.get('/roles')
def get_roles():
    return list_roles()
