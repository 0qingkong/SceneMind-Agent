from __future__ import annotations

import re

from app.agent.schemas import AgentPlan

_NUMBER_WORDS = {
    "一": 1, "二": 2, "两": 2, "三": 3, "四": 4,
    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
}

_OBJECT_ALIASES = {
    "笔记本电脑": "电脑", "计算机": "电脑", "computer": "laptop",
    "notebook": "laptop", "laptop": "laptop", "电脑": "电脑",
    "cell phone": "手机", "smartphone": "手机", "phone": "手机", "手机": "手机",
    "人物": "人物", "people": "person", "person": "person",
    "杯子": "杯子", "水杯": "杯子", "mug": "cup", "cup": "cup",
    "椅子": "椅子", "chairs": "chair", "chair": "chair",
    "背包": "背包", "backpack": "backpack", "瓶子": "瓶子", "bottle": "bottle",
    "书本": "书", "books": "book", "book": "book", "书": "书", "人": "人物",
}


def _extract_limit(query: str, default: int, maximum: int) -> int:
    digit_match = re.search(
        r"(?:最近|latest|recent|show|展示)?\s*(\d{1,3})\s*(?:条|个|records?|scenes?|memories)?",
        query,
        re.I,
    )
    if digit_match:
        return max(1, min(int(digit_match.group(1)), maximum))
    word_match = re.search(r"最近([一二两三四五六七八九十])条", query)
    if word_match:
        return min(_NUMBER_WORDS[word_match.group(1)], maximum)
    return min(default, maximum)


def _extract_object(query: str) -> str | None:
    lowered = query.casefold()
    for alias in sorted(_OBJECT_ALIASES, key=len, reverse=True):
        if alias.casefold() in lowered:
            return _OBJECT_ALIASES[alias]
    return None


def _extract_observation_ref(query: str) -> str | None:
    cleaned = query.strip().strip("？?。.!！")
    suffixes = (
        "那条记录里检测到了什么", "那条记录里有什么", "记录里检测到了什么",
        "记录里有什么", "场景里检测到了什么", "场景里有什么",
    )
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            reference = cleaned[: -len(suffix)].strip(" 的")
            return reference or None
    english = re.search(
        r"(?:what (?:was )?(?:detected|is|was) (?:in|at)|show (?:the )?(?:record|observation) (?:for|at))\s+(.+?)(?:\s+(?:record|observation|scene))?$",
        cleaned,
        re.I,
    )
    if not english:
        return None
    reference = english.group(1).strip()
    return re.sub(r"^the\s+", "", reference, flags=re.I)


def _extract_location(query: str) -> str | None:
    chinese = re.search(r"在(.+?)(?:一共|总共|检测到|有多少)", query)
    if chinese:
        return chinese.group(1).strip(" 的") or None
    english = re.search(r"\b(?:in|at)\s+([a-z0-9 _-]+?)(?:[?.!]|$)", query, re.I)
    if english:
        return re.sub(r"^the\s+", "", english.group(1).strip(), flags=re.I)
    return None


class AgentPlanner:
    def __init__(self, *, default_limit: int = 3, max_limit: int = 20) -> None:
        self.default_limit = default_limit
        self.max_limit = max_limit

    def plan(self, query: str) -> AgentPlan:
        cleaned = " ".join(query.strip().split())
        if not cleaned:
            raise ValueError("query must not be empty")
        lowered = cleaned.casefold()
        limit = _extract_limit(cleaned, self.default_limit, self.max_limit)
        object_query = _extract_object(cleaned)

        if any(token in lowered for token in ("帮助", "怎么问", "help", "examples", "能做什么")):
            return AgentPlan(intent="help", limit=limit)
        if any(token in lowered for token in ("最后出现", "最后看到", "last seen", "where was", "where is my")):
            if object_query:
                return AgentPlan(intent="last_seen", object_query=object_query, limit=1)
        if any(token in lowered for token in ("哪些场景", "历史", "history", "seen", "见过")) and object_query:
            return AgentPlan(intent="history", object_query=object_query, limit=limit)
        if any(token in lowered for token in ("一共", "总共", "多少", "how many", "count")):
            return AgentPlan(
                intent="object_count",
                object_query=object_query,
                location=_extract_location(cleaned),
                limit=limit,
            )
        observation_ref = _extract_observation_ref(cleaned)
        if observation_ref:
            return AgentPlan(intent="observation_detail", observation_ref=observation_ref, limit=1)
        if any(token in lowered for token in ("最近", "展示", "场景记忆", "recent observations", "recent scenes", "latest memories")) and any(
            token in lowered for token in ("记录", "记忆", "场景", "observations", "scenes", "memories")
        ):
            return AgentPlan(intent="recent_observations", limit=limit)
        return AgentPlan(intent="unknown", limit=limit)
