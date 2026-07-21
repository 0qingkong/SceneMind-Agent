COCO_DISPLAY_NAMES: dict[str, str] = {
    "person": "人",
    "chair": "椅子",
    "couch": "沙发",
    "bed": "床",
    "dining table": "餐桌",
    "laptop": "笔记本电脑",
    "keyboard": "键盘",
    "mouse": "鼠标",
    "cell phone": "手机",
    "book": "书",
    "backpack": "背包",
    "handbag": "手提包",
    "bottle": "瓶子",
    "cup": "杯子",
    "bowl": "碗",
    "clock": "时钟",
    "tv": "电视",
}


def get_display_name(class_name: str) -> str:
    """Return a localized COCO name, preserving unknown English labels."""

    return COCO_DISPLAY_NAMES.get(class_name.casefold(), class_name)
