from __future__ import annotations

from app.agent.formatter import (
    HELP_ANSWER,
    UNKNOWN_ANSWER,
    format_count,
    format_detail,
    format_history,
    format_last_seen,
    format_recent,
    limitations_for,
)
from app.agent.planner import AgentPlanner
from app.agent.schemas import AgentQueryResponse, EvidenceCard, ToolStep
from app.agent.tools import AgentTools, evidence_from_match
from app.services.memory_service import MemoryNotFoundError


class AgentExecutor:
    def __init__(self, planner: AgentPlanner, tools: AgentTools) -> None:
        self.planner = planner
        self.tools = tools

    def execute(self, query: str) -> AgentQueryResponse:
        cleaned = query.strip()
        plan = self.planner.plan(cleaned)
        evidence: list[EvidenceCard] = []
        steps: list[ToolStep] = []

        if plan.intent == "last_seen":
            assert plan.object_query is not None
            try:
                result = self.tools.memory_last_seen(plan.object_query)
                evidence = [evidence_from_match(result.result)]
            except MemoryNotFoundError:
                evidence = []
            steps.append(self._step("memory_last_seen", {"query": plan.object_query}, evidence))
            answer = format_last_seen(plan.object_query, evidence)
        elif plan.intent == "history":
            assert plan.object_query is not None
            result = self.tools.memory_history(plan.object_query, plan.limit, 0)
            evidence = [evidence_from_match(item) for item in result.items]
            steps.append(
                self._step(
                    "memory_history",
                    {"query": plan.object_query, "limit": plan.limit, "offset": 0},
                    evidence,
                )
            )
            answer = format_history(plan.object_query, evidence, result.total)
        elif plan.intent == "recent_observations":
            result = self.tools.list_recent_observations(plan.limit)
            evidence = [
                EvidenceCard(
                    observation_id=item.id,
                    title=item.title,
                    location=item.location,
                    timestamp=item.created_at,
                    image_url=item.image_url,
                    detail_url=item.detail_url,
                    is_demo=item.is_demo,
                )
                for item in result.items
            ]
            steps.append(self._step("list_recent_observations", {"limit": plan.limit}, evidence))
            answer = format_recent(evidence, result.total)
        elif plan.intent == "observation_detail":
            assert plan.observation_ref is not None
            detail = self.tools.get_observation_detail(plan.observation_ref)
            item = self.tools.detail_evidence(plan.observation_ref)
            evidence = [item] if item else []
            steps.append(
                self._step(
                    "get_observation_detail",
                    {"id_or_text": plan.observation_ref},
                    evidence,
                )
            )
            answer = format_detail(
                plan.observation_ref,
                detail.summary if detail else None,
                evidence,
            )
        elif plan.intent == "object_count":
            result = self.tools.count_objects(plan.object_query, plan.location)
            evidence = result.matches
            steps.append(
                ToolStep(
                    tool="count_objects",
                    arguments={"query": plan.object_query, "location": plan.location},
                    status="success" if result.count else "no_match",
                    result_count=result.count,
                )
            )
            answer = format_count(plan.object_query, plan.location, result.count)
        elif plan.intent == "help":
            answer = HELP_ANSWER
            steps.append(ToolStep(tool="none", status="skipped"))
        else:
            answer = UNKNOWN_ANSWER
            steps.append(ToolStep(tool="none", status="skipped"))

        return AgentQueryResponse(
            query=cleaned,
            intent=plan.intent,
            answer=answer,
            tool_steps=steps,
            evidence=evidence,
            limitations=limitations_for(plan.intent, evidence),
        )

    @staticmethod
    def _step(
        name: str,
        arguments: dict[str, str | int | None],
        evidence: list[EvidenceCard],
    ) -> ToolStep:
        return ToolStep(
            tool=name,
            arguments=arguments,
            status="success" if evidence else "no_match",
            result_count=len(evidence),
        )
