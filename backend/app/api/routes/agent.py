from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.agent.executor import AgentExecutor
from app.agent.schemas import AgentQueryRequest, AgentQueryResponse
from app.dependencies import get_agent_executor

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query", response_model=AgentQueryResponse)
def query_agent(
    request: AgentQueryRequest,
    executor: Annotated[AgentExecutor, Depends(get_agent_executor)],
) -> AgentQueryResponse:
    try:
        return executor.execute(request.query)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
