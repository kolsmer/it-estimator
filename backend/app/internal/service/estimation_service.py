from decimal import Decimal
from typing import Optional

from backend.app.internal.domain.enums import ComplexityLevel, RoleType, SeniorityLevel
from backend.app.internal.domain.models import ProjectEstimate, ProjectInput, ProjectStage, RoleAssignment
from backend.app.internal.service.estimator_config import ConfigLoader


def process_data(df):
    return df.describe()


class ProjectEstimator:
    def __init__(self, config_path: str = "project_estimator.json"):
        self.config = ConfigLoader(config_path)

    def estimate(self, project_input: ProjectInput, similar_projects_count: int = 0) -> ProjectEstimate:
        base_hours = self._calculate_base_hours(project_input)
        total_hours = self._apply_complexity(base_hours, project_input)
        overall_complexity = self._determine_overall_complexity(project_input)

        role_assignments = self._distribute_roles(
            total_hours,
            project_input.get_project_type_value(),
            overall_complexity,
        )

        total_cost_rub = Decimal('0')
        for assignment in role_assignments:
            total_cost_rub += assignment.cost_rub

        duration_weeks, team_size = self._calculate_timeline(role_assignments, project_input.deadline_weeks)

        if total_hours > 0:
            avg_rate_rub = total_cost_rub / Decimal(str(total_hours))
        else:
            avg_rate_rub = Decimal('0')

        stages = self._generate_stages(project_input, total_cost_rub)
        confidence = self._calculate_confidence(project_input, similar_projects_count)

        return ProjectEstimate(
            total_cost_rub=total_cost_rub.quantize(Decimal('0.01')),
            total_hours=total_hours,
            duration_weeks=duration_weeks,
            team_size=team_size,
            roles=role_assignments,
            hourly_rate_avg_rub=avg_rate_rub.quantize(Decimal('0.01')),
            stages=stages,
            project_name=project_input.name,
            project_type=project_input.get_project_type_value(),
            currency=project_input.currency,
            confidence_score=confidence,
            similar_projects_found=similar_projects_count,
        )

    def _calculate_base_hours(self, project_input: ProjectInput) -> int:
        rules = self.config.get_calculation_rules()
        base = self.config.get_project_type_base_hours(project_input.get_project_type_value())
        feature_base = rules.get('feature_base_hours', 20)

        feature_hours = 0
        for feature in project_input.features:
            multiplier = self.config.get_complexity_multiplier(feature.get_complexity_value())
            feature_hours += int(feature_base * multiplier)

        return base + feature_hours

    def _apply_complexity(self, hours: int, project_input: ProjectInput) -> int:
        multipliers = [
            self.config.get_complexity_multiplier(project_input.get_design_complexity_value()),
            self.config.get_complexity_multiplier(project_input.get_backend_complexity_value()),
            self.config.get_complexity_multiplier(project_input.get_frontend_complexity_value()),
        ]
        avg_multiplier = sum(multipliers) / len(multipliers)
        return int(hours * avg_multiplier)

    def _determine_overall_complexity(self, project_input: ProjectInput) -> str:
        complexities = [
            project_input.get_design_complexity_value(),
            project_input.get_backend_complexity_value(),
            project_input.get_frontend_complexity_value(),
        ]

        if ComplexityLevel.CRITICAL.value in complexities:
            return ComplexityLevel.CRITICAL.value

        high_count = complexities.count(ComplexityLevel.HIGH.value)
        if high_count >= 2:
            return ComplexityLevel.HIGH.value

        if ComplexityLevel.HIGH.value in complexities:
            return ComplexityLevel.HIGH.value

        return ComplexityLevel.MEDIUM.value

    def _distribute_roles(self, total_hours: int, project_type: str, overall_complexity: str) -> list[RoleAssignment]:
        distribution = self.config.get_role_distribution(project_type)
        seniority_dist = self.config.get_seniority_distribution(overall_complexity)

        assignments = []

        for role, percentage in distribution.items():
            role_hours = int(total_hours * percentage)
            for seniority, seniority_percent in seniority_dist.items():
                if seniority_percent > 0 and role_hours > 0:
                    seniority_hours = int(role_hours * seniority_percent)
                    if seniority_hours > 0:
                        rate_rub = self.config.get_rate_rub(role, seniority)
                        assignments.append(
                            RoleAssignment(
                                role=RoleType(role),
                                role_name=self.config.get_role_name(role),
                                seniority=SeniorityLevel(seniority),
                                seniority_name=self.config.get_seniority_name(seniority),
                                hours=seniority_hours,
                                count=1,
                                rate_per_hour_rub=rate_rub,
                            )
                        )
        return assignments

    def _calculate_timeline(
        self,
        role_assignments: list[RoleAssignment],
        deadline_weeks: Optional[int] = None,
    ) -> tuple[int, int]:
        rules = self.config.get_calculation_rules()
        hours_per_week = rules.get('hours_per_week', 40)

        total_person_hours = sum(assignment.total_hours for assignment in role_assignments)
        unique_roles = len(set(assignment.get_role_value() for assignment in role_assignments))

        if deadline_weeks:
            hours_per_week_needed = total_person_hours / deadline_weeks
            team_size = max(unique_roles, int(hours_per_week_needed / hours_per_week) + 1)
            return deadline_weeks, team_size

        weeks = int(total_person_hours / (hours_per_week * unique_roles)) + 1
        return weeks, unique_roles

    def _generate_stages(self, project_input: ProjectInput, total_cost_rub: Decimal) -> dict[str, ProjectStage]:
        stages_config = self.config.get_project_stages()
        stages = {}
        for stage_id, stage_data in stages_config.items():
            percentage = stage_data['percentage']
            stages[stage_id] = ProjectStage(
                name=stage_data['name'],
                percentage=percentage,
                cost_rub=(total_cost_rub * Decimal(str(percentage))).quantize(Decimal('0.01')),
                duration_weeks=stage_data['duration_weeks'],
            )
        return stages

    def _calculate_confidence(self, project_input: ProjectInput, similar_projects: int) -> float:
        factors = self.config.get_confidence_factors()
        confidence = factors.get('base_confidence', 0.5)
        per_project = factors.get('per_similar_project', 0.05)
        max_boost = factors.get('max_similar_projects_boost', 0.3)
        confidence += min(max_boost, similar_projects * per_project)

        if project_input.deadline_weeks:
            confidence += factors.get('deadline_boost', 0.1)
        if project_input.budget_min_rub and project_input.budget_max_rub:
            confidence += factors.get('budget_boost', 0.1)

        return min(1.0, confidence)


class EstimationFacade:
    def __init__(self, config_path: str = "project_estimator.json"):
        self.estimator = ProjectEstimator(config_path)
        self.config = ConfigLoader(config_path)

    def estimate_from_ai_input(self, ai_json_input: dict) -> dict:
        try:
            if 'currency' not in ai_json_input:
                ai_json_input['currency'] = self.config.currency

            project_input = ProjectInput(**ai_json_input)
            similar_projects = ai_json_input.get('similar_projects_found', 0)
            estimate = self.estimator.estimate(project_input, similar_projects)

            return {
                "success": True,
                "data": estimate.model_dump_for_json(),
                "message": "Расчёт успешно выполнен",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Ошибка при расчёте проекта",
            }
