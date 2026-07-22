from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import Observation, ObservedObject, ObservedRelation
from app.repositories.observations import ObservationRepository, observation_summary
from app.schemas.memory import (
    HistoryResponse,
    LastSeenResponse,
    MemoryMatch,
    RelationContext,
)
from app.services.object_names import build_object_name_map


class MemoryNotFoundError(LookupError):
    pass


_QUERY_ALIASES = {
    "人物": ("人物", "人", "person"),
    "人": ("人", "person"),
    "电脑": ("电脑", "笔记本电脑", "laptop"),
    "笔记本": ("笔记本", "笔记本电脑", "laptop"),
    "手机": ("手机", "cell phone"),
    "杯子": ("杯子", "cup"),
    "背包": ("背包", "backpack"),
}


def _search_terms(query: str) -> tuple[str, ...]:
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("q must not be empty")
    aliases = _QUERY_ALIASES.get(cleaned)
    return tuple(dict.fromkeys((cleaned, *(aliases or ()))))


def _matches(item: ObservedObject, terms: Iterable[str]) -> bool:
    label = item.label.casefold()
    display_name = item.display_name.casefold()
    return any(
        term.casefold() in label or term.casefold() in display_name for term in terms
    )


def _reciprocal_key(relation: ObservedRelation) -> tuple[str, str, str]:
    subject_id, object_id = relation.subject_id, relation.object_id
    if relation.predicate == "left_of":
        return "horizontal", subject_id, object_id
    if relation.predicate == "right_of":
        return "horizontal", object_id, subject_id
    if relation.predicate == "above":
        return "vertical", subject_id, object_id
    if relation.predicate == "below":
        return "vertical", object_id, subject_id
    if relation.predicate == "inside":
        return "containment", subject_id, object_id
    if relation.predicate == "contains":
        return "containment", object_id, subject_id
    first_id, second_id = sorted((subject_id, object_id))
    return relation.predicate, first_id, second_id


class MemoryService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self.repository = ObservationRepository(session)
        self.settings = settings

    def last_seen(self, query: str) -> LastSeenResponse:
        terms = _search_terms(query)
        observations, _ = self.repository.matching(terms=terms, limit=1, offset=0)
        if not observations:
            raise MemoryNotFoundError(f"No observation matched {query!r}")
        match = self._memory_match(observations[0], terms)
        matched_labels = list(
            dict.fromkeys(
                item.label for item in observations[0].objects if _matches(item, terms)
            )
        )
        return LastSeenResponse(
            query=query.strip(),
            matched_labels=matched_labels,
            result=match,
        )

    def history(
        self,
        *,
        query: str,
        limit: int,
        offset: int,
    ) -> HistoryResponse:
        terms = _search_terms(query)
        observations, total = self.repository.matching(
            terms=terms,
            limit=limit,
            offset=offset,
        )
        return HistoryResponse(
            query=query.strip(),
            items=[self._memory_match(item, terms) for item in observations],
            total=total,
            limit=limit,
            offset=offset,
        )

    def _memory_match(
        self,
        observation: Observation,
        terms: tuple[str, ...],
    ) -> MemoryMatch:
        matched_objects = [item for item in observation.objects if _matches(item, terms)]
        matched_ids = {item.id for item in matched_objects}
        names = build_object_name_map(observation.objects)
        relation_context = self._relation_context(
            observation.relations,
            matched_ids,
            names,
        )
        return MemoryMatch(
            observation=observation_summary(observation),
            matched_object_ids=[item.id for item in matched_objects],
            matched_names=[names[item.id] for item in matched_objects],
            relations=relation_context,
        )

    def _relation_context(
        self,
        relations: Iterable[ObservedRelation],
        matched_ids: set[str],
        names: dict[str, str],
    ) -> list[RelationContext]:
        relevant = sorted(
            (
                relation
                for relation in relations
                if relation.subject_id in matched_ids or relation.object_id in matched_ids
            ),
            key=lambda item: (-item.score, item.predicate, item.subject_id, item.object_id),
        )
        seen: set[tuple[str, str, str]] = set()
        result: list[RelationContext] = []
        for relation in relevant:
            key = _reciprocal_key(relation)
            if key in seen:
                continue
            seen.add(key)
            result.append(
                RelationContext(
                    relation_id=relation.id,
                    subject_id=relation.subject_id,
                    subject_name=names.get(relation.subject_id, relation.subject_id),
                    predicate=relation.predicate,
                    object_id=relation.object_id,
                    object_name=names.get(relation.object_id, relation.object_id),
                    score=relation.score,
                )
            )
            if len(result) >= self.settings.memory_relation_context_limit:
                break
        return result
