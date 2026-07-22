from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol


class NameableObject(Protocol):
    id: str
    label: str
    display_name: str
    sort_order: int


def build_object_name_map(objects: Iterable[NameableObject]) -> dict[str, str]:
    ordered = sorted(objects, key=lambda item: item.sort_order)
    base_names = {
        item.id: "人物" if item.label.casefold() == "person" else item.display_name
        for item in ordered
    }
    totals: dict[str, int] = {}
    for name in base_names.values():
        totals[name] = totals.get(name, 0) + 1
    ordinals: dict[str, int] = {}
    resolved: dict[str, str] = {}
    for item in ordered:
        name = base_names[item.id]
        if totals[name] == 1:
            resolved[item.id] = name
            continue
        ordinals[name] = ordinals.get(name, 0) + 1
        resolved[item.id] = f"{name} {ordinals[name]}"
    return resolved
