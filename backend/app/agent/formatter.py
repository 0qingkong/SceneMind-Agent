from __future__ import annotations

from app.agent.schemas import AgentIntent, EvidenceCard

CATEGORY_LIMITATION = "基于检测类别匹配，不能证明不同图片中是同一个现实物体。"
SPATIAL_LIMITATION = "二维图像关系不能证明真实深度或物理距离。"


def limitations_for(intent: AgentIntent, evidence: list[EvidenceCard]) -> list[str]:
    limitations: list[str] = []
    if intent in {"last_seen", "history", "object_count"}:
        limitations.append(CATEGORY_LIMITATION)
    if any(item.relation_context for item in evidence):
        limitations.append(SPATIAL_LIMITATION)
    return limitations


def scene_name(evidence: EvidenceCard) -> str:
    return evidence.title or evidence.location or "未命名场景"


def format_last_seen(query: str, evidence: list[EvidenceCard]) -> str:
    if not evidence:
        return f"没有找到包含“{query}”的场景记忆。"
    item = evidence[0]
    location = f"，位置为{item.location}" if item.location else ""
    return f"最近一次在“{scene_name(item)}”中检测到{query}{location}。请查看下方图片证据。"


def format_history(query: str, evidence: list[EvidenceCard], total: int) -> str:
    if not evidence:
        return f"没有找到包含“{query}”的历史场景。"
    return f"共找到 {total} 条包含“{query}”的场景记忆，下面按时间从新到旧展示 {len(evidence)} 条。"


def format_recent(evidence: list[EvidenceCard], total: int) -> str:
    if not evidence:
        return "当前还没有保存任何场景记忆。"
    return f"当前共有 {total} 条场景记忆，下面展示最近 {len(evidence)} 条。"


def format_detail(reference: str, detail_summary: str | None, evidence: list[EvidenceCard]) -> str:
    if not evidence:
        return f"没有找到标题或位置包含“{reference}”的场景记录。"
    objects = "、".join(evidence[0].matched_objects) or "没有物体"
    summary = f"记录摘要：{detail_summary} " if detail_summary else ""
    return f"{summary}检测到：{objects}。"


def format_count(query: str | None, location: str | None, count: int) -> str:
    target = query or "物体"
    scope = f"在位置“{location}”的记忆中" if location else "在全部场景记忆中"
    return f"{scope}一共检测到 {count} 个{target}。这是检测次数总和，不是现实物体去重数量。"


HELP_ANSWER = (
    "我可以查询物体最后出现位置、历史场景、最近场景、指定记录内容和检测数量。"
    "例如：‘我的杯子最后出现在哪里？’或‘展示最近三条场景记忆’。"
)

UNKNOWN_ANSWER = "这个问题超出当前空间记忆检索范围。你可以询问最后出现、历史场景、最近记录、记录详情或检测数量。"
