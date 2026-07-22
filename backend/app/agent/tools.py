from __future__ import annotations

from app.agent.schemas import EvidenceCard, ObjectCountResult
from app.core.config import Settings
from app.repositories.observations import (
    ObservationRepository,
    observation_detail,
    observation_summary,
)
from app.schemas.memory import HistoryResponse, LastSeenResponse, MemoryMatch
from app.schemas.observation import ObservationDetail, ObservationListResponse
from app.services.memory_service import MemoryService, search_terms


def evidence_from_match(match: MemoryMatch) -> EvidenceCard:
    observation = match.observation
    return EvidenceCard(
        observation_id=observation.id,
        title=observation.title,
        location=observation.location,
        timestamp=observation.created_at,
        image_url=observation.image_url,
        detail_url=observation.detail_url,
        matched_objects=match.matched_names,
        relation_context=match.relations,
        is_demo=observation.is_demo,
    )


class AgentTools:
    """Structured, read-only wrappers around the existing memory services."""

    def __init__(self, memory: MemoryService, settings: Settings) -> None:
        self.memory = memory
        self.settings = settings
        self.repository: ObservationRepository = memory.repository

    def memory_last_seen(self, query: str) -> LastSeenResponse:
        return self.memory.last_seen(query)

    def memory_history(self, query: str, limit: int, offset: int) -> HistoryResponse:
        return self.memory.history(query=query, limit=limit, offset=offset)

    def list_recent_observations(self, limit: int) -> ObservationListResponse:
        items, total = self.repository.list(limit=limit, offset=0)
        return ObservationListResponse(
            items=[observation_summary(item) for item in items],
            total=total,
            limit=limit,
            offset=0,
        )

    def get_observation_detail(self, id_or_text: str) -> ObservationDetail | None:
        model = self.repository.find_reference(id_or_text)
        return observation_detail(model) if model else None

    def detail_evidence(self, id_or_text: str) -> EvidenceCard | None:
        model = self.repository.find_reference(id_or_text)
        return evidence_from_match(self.memory.match_all_objects(model)) if model else None

    def count_objects(
        self,
        query: str | None = None,
        location: str | None = None,
    ) -> ObjectCountResult:
        terms = search_terms(query) if query else None
        count = self.repository.count_objects(terms=terms, location=location)
        if terms:
            observations, _ = self.repository.matching(
                terms=terms,
                limit=self.settings.observation_max_limit,
                offset=0,
                location=location,
            )
        else:
            observations, _ = self.repository.list(
                limit=self.settings.observation_max_limit,
                offset=0,
                query=location,
            )
        if location:
            observations = [
                item
                for item in observations
                if item.location and location.casefold() in item.location.casefold()
            ]
        matches = [
            evidence_from_match(
                self.memory.match_observation(item, terms)
                if terms
                else self.memory.match_all_objects(item)
            )
            for item in observations
        ]
        return ObjectCountResult(
            query=query,
            location=location,
            count=count,
            matches=matches,
        )
