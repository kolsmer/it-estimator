from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.app.internal.domain.enums import ComplexityLevel, ProjectType, RoleType, SeniorityLevel


class Feature(BaseModel):
    name: str
    complexity: ComplexityLevel
    description: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)

    def get_complexity_value(self) -> str:
        if isinstance(self.complexity, ComplexityLevel):
            return self.complexity.value
        return str(self.complexity)


class ProjectInput(BaseModel):
    project_type: ProjectType
    name: str
    description: str
    features: list[Feature] = Field(default_factory=list)
    design_complexity: ComplexityLevel
    backend_complexity: ComplexityLevel
    frontend_complexity: ComplexityLevel
    deadline_weeks: Optional[int] = Field(None, ge=1, le=104)
    budget_min_rub: Optional[Decimal] = Field(None, ge=0)
    budget_max_rub: Optional[Decimal] = Field(None, ge=0)
    target_platforms: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)
    currency: str = Field(default="RUB")

    model_config = ConfigDict(use_enum_values=True)

    @field_validator('budget_max_rub')
    @classmethod
    def validate_budget(cls, value, info):
        if value is not None and 'budget_min_rub' in info.data and info.data['budget_min_rub'] is not None:
            if value < info.data['budget_min_rub']:
                raise ValueError('budget_max_rub must be >= budget_min_rub')
        return value

    def get_project_type_value(self) -> str:
        if isinstance(self.project_type, ProjectType):
            return self.project_type.value
        return str(self.project_type)

    def get_design_complexity_value(self) -> str:
        if isinstance(self.design_complexity, ComplexityLevel):
            return self.design_complexity.value
        return str(self.design_complexity)

    def get_backend_complexity_value(self) -> str:
        if isinstance(self.backend_complexity, ComplexityLevel):
            return self.backend_complexity.value
        return str(self.backend_complexity)

    def get_frontend_complexity_value(self) -> str:
        if isinstance(self.frontend_complexity, ComplexityLevel):
            return self.frontend_complexity.value
        return str(self.frontend_complexity)


class RoleAssignment(BaseModel):
    role: RoleType
    role_name: str
    seniority: SeniorityLevel
    seniority_name: str
    hours: int = Field(ge=0, le=10000)
    count: int = Field(ge=1, le=20, default=1)
    rate_per_hour_rub: Decimal

    model_config = ConfigDict(use_enum_values=True, arbitrary_types_allowed=True)

    @property
    def total_hours(self) -> int:
        return self.hours * self.count

    @property
    def cost_rub(self) -> Decimal:
        return (self.rate_per_hour_rub * self.total_hours).quantize(Decimal('0.01'))

    def get_role_value(self) -> str:
        if isinstance(self.role, RoleType):
            return self.role.value
        return str(self.role)

    def get_seniority_value(self) -> str:
        if isinstance(self.seniority, SeniorityLevel):
            return self.seniority.value
        return str(self.seniority)

    def dict_for_json(self) -> dict:
        return {
            "role": self.get_role_value(),
            "role_name": self.role_name,
            "seniority": self.get_seniority_value(),
            "seniority_name": self.seniority_name,
            "hours": self.hours,
            "count": self.count,
            "total_hours": self.total_hours,
            "rate_per_hour_rub": float(self.rate_per_hour_rub),
            "cost_rub": float(self.cost_rub),
        }


class ProjectStage(BaseModel):
    name: str
    percentage: float
    cost_rub: Decimal
    duration_weeks: int

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def dict_for_json(self) -> dict:
        return {
            "name": self.name,
            "percentage": self.percentage,
            "cost_rub": float(self.cost_rub),
            "duration_weeks": self.duration_weeks,
        }


class ProjectEstimate(BaseModel):
    total_cost_rub: Decimal
    total_hours: int
    duration_weeks: int
    team_size: int
    roles: list[RoleAssignment]
    hourly_rate_avg_rub: Decimal
    stages: dict[str, ProjectStage]
    project_name: str
    project_type: str
    currency: str
    confidence_score: float = Field(ge=0, le=1.0)
    similar_projects_found: int
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def model_dump_for_json(self) -> dict:
        return {
            "total_cost_rub": float(self.total_cost_rub),
            "total_hours": self.total_hours,
            "duration_weeks": self.duration_weeks,
            "team_size": self.team_size,
            "roles": [role.dict_for_json() for role in self.roles],
            "hourly_rate_avg_rub": float(self.hourly_rate_avg_rub),
            "stages": {key: value.dict_for_json() for key, value in self.stages.items()},
            "project_name": self.project_name,
            "project_type": self.project_type,
            "currency": self.currency,
            "confidence_score": self.confidence_score,
            "similar_projects_found": self.similar_projects_found,
            "created_at": self.created_at.isoformat(),
        }
