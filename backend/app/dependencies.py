from app.core.config import Settings
from app.services.analyzers import SceneAnalyzer, create_analyzer
from app.services.spatial import SpatialReasoner

settings = Settings.from_env()
analyzer = create_analyzer(settings)
spatial_reasoner = SpatialReasoner.from_settings(settings)


def get_settings() -> Settings:
    return settings


def get_analyzer() -> SceneAnalyzer:
    return analyzer


def get_spatial_reasoner() -> SpatialReasoner:
    return spatial_reasoner
