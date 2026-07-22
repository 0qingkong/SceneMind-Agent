from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db import Database
from app.services.analyzers import SceneAnalyzer, create_analyzer
from app.services.analysis_service import AnalysisService
from app.services.image_storage import ImageStorage
from app.services.observation_service import ObservationService
from app.services.spatial import SpatialReasoner

settings = Settings.from_env()
analyzer = create_analyzer(settings)
spatial_reasoner = SpatialReasoner.from_settings(settings)
database = Database(settings.database_url)
image_storage = ImageStorage(settings.scene_storage_dir)
analysis_service = AnalysisService(analyzer, spatial_reasoner)


def get_settings() -> Settings:
    return settings


def get_analyzer() -> SceneAnalyzer:
    return analyzer


def get_spatial_reasoner() -> SpatialReasoner:
    return spatial_reasoner


def get_database() -> Database:
    return database


def get_db_session() -> Iterator[Session]:
    yield from database.sessions()


def get_image_storage() -> ImageStorage:
    return image_storage


def get_analysis_service() -> AnalysisService:
    return analysis_service


def get_observation_service(
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[AnalysisService, Depends(get_analysis_service)],
    storage: Annotated[ImageStorage, Depends(get_image_storage)],
) -> ObservationService:
    return ObservationService(session, service, storage)
