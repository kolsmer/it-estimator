from enum import Enum


class ProjectType(str, Enum):
    WEBSITE = "website"
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    ECOMMERCE = "ecommerce"
    MARKETPLACE = "marketplace"
    CRM = "crm"
    ERP = "erp"
    API = "api"
    CHATBOT = "chatbot"
    AI_SERVICE = "ai_service"
    OTHER = "other"


class ComplexityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoleType(str, Enum):
    PROJECT_MANAGER = "project_manager"
    BUSINESS_ANALYST = "business_analyst"
    UX_UI_DESIGNER = "ux_ui_designer"
    FRONTEND_DEVELOPER = "frontend_developer"
    BACKEND_DEVELOPER = "backend_developer"
    FULLSTACK_DEVELOPER = "fullstack_developer"
    MOBILE_DEVELOPER = "mobile_developer"
    DEVOPS = "devops"
    QA_ENGINEER = "qa_engineer"
    DATA_SCIENTIST = "data_scientist"
    ML_ENGINEER = "ml_engineer"
    ARCHITECT = "architect"


class SeniorityLevel(str, Enum):
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"
