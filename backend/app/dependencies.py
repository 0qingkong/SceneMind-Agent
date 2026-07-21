from app.core.config import Settings
from app.services.analyzers import SceneAnalyzer, create_analyzer

settings = Settings.from_env()
analyzer = create_analyzer(settings)


def get_settings() -> Settings:
    return settings


def get_analyzer() -> SceneAnalyzer:
    return analyzer
