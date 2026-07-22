from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from app.repositories.observations import ObservationRepository
from app.schemas.analyze import (
    AnalyzeResponse,
    DetectedObject,
    DetectedRelation,
    RelationEvidence,
)
from app.services.image_storage import ImageStorage


@dataclass(frozen=True, slots=True)
class DemoScene:
    observation_id: str
    title: str
    location: str
    filename: str
    objects: tuple[DetectedObject, ...]
    relations: tuple[DetectedRelation, ...]


def _object(
    object_id: str,
    label: str,
    display_name: str,
    confidence: float,
    bbox: list[float],
) -> DetectedObject:
    return DetectedObject(
        id=object_id,
        label=label,
        display_name=display_name,
        confidence=confidence,
        bbox=bbox,
    )


def _relation(
    relation_id: str,
    subject_id: str,
    predicate: str,
    object_id: str,
    score: float,
) -> DetectedRelation:
    return DetectedRelation(
        id=relation_id,
        subject_id=subject_id,
        predicate=predicate,  # type: ignore[arg-type]
        object_id=object_id,
        score=score,
        evidence=RelationEvidence(method="geometry", center_distance=0.32),
    )


DEMO_SCENES = (
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000101",
        title="[演示] 桌面工作区",
        location="共享办公室",
        filename="demo-desk.png",
        objects=(
            _object("cup-1", "cup", "杯子", 0.94, [0.08, 0.48, 0.24, 0.78]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.96, [0.34, 0.24, 0.78, 0.72]),
            _object("book-1", "book", "书", 0.88, [0.68, 0.72, 0.90, 0.86]),
        ),
        relations=(
            _relation("desk-r1", "cup-1", "left_of", "laptop-1", 0.86),
            _relation("desk-r2", "laptop-1", "right_of", "cup-1", 0.86),
            _relation("desk-r3", "book-1", "below", "laptop-1", 0.72),
            _relation("desk-r4", "laptop-1", "above", "book-1", 0.72),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000102",
        title="[演示] 图书馆阅读区",
        location="图书馆",
        filename="demo-library.png",
        objects=(
            _object("person-1", "person", "人", 0.95, [0.10, 0.14, 0.35, 0.86]),
            _object("chair-1", "chair", "椅子", 0.91, [0.08, 0.58, 0.40, 0.94]),
            _object("book-1", "book", "书", 0.89, [0.52, 0.48, 0.72, 0.64]),
        ),
        relations=(
            _relation("library-r1", "person-1", "left_of", "book-1", 0.79),
            _relation("library-r2", "book-1", "right_of", "person-1", 0.79),
            _relation("library-r3", "person-1", "overlaps", "chair-1", 0.63),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000103",
        title="[演示] 智慧教室",
        location="教学楼 201",
        filename="demo-classroom.png",
        objects=(
            _object("person-1", "person", "人", 0.96, [0.08, 0.18, 0.28, 0.82]),
            _object("person-2", "person", "人", 0.93, [0.38, 0.20, 0.58, 0.83]),
            _object("chair-1", "chair", "椅子", 0.90, [0.06, 0.60, 0.31, 0.94]),
            _object("chair-2", "chair", "椅子", 0.87, [0.36, 0.62, 0.61, 0.95]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.91, [0.68, 0.40, 0.91, 0.64]),
        ),
        relations=(
            _relation("class-r1", "person-1", "left_of", "person-2", 0.82),
            _relation("class-r2", "person-2", "right_of", "person-1", 0.82),
            _relation("class-r3", "person-2", "left_of", "laptop-1", 0.70),
            _relation("class-r4", "laptop-1", "right_of", "person-2", 0.70),
        ),
    ),
)


class DemoDataService:
    def __init__(self, session: Session, storage: ImageStorage) -> None:
        self.session = session
        self.storage = storage
        self.repository = ObservationRepository(session)

    def seed(self) -> int:
        created = 0
        base_time = datetime.now(timezone.utc) - timedelta(hours=len(DEMO_SCENES))
        for index, scene in enumerate(DEMO_SCENES):
            if self.repository.get(scene.observation_id) is not None:
                continue
            image_bytes = self._render_scene(scene)
            image_path = self.storage.save(image_bytes, "image/png")
            analysis = AnalyzeResponse(
                trace_id=f"demo-{scene.observation_id}",
                engine="demo-seed",
                filename=scene.filename,
                image_width=960,
                image_height=640,
                scene_summary=self._summary(scene),
                objects=list(scene.objects),
                relations=list(scene.relations),
                latency_ms=0,
            )
            try:
                self.repository.create(
                    observation_id=scene.observation_id,
                    title=scene.title,
                    location=scene.location,
                    created_at=base_time + timedelta(hours=index),
                    image_path=image_path,
                    mime_type="image/png",
                    analysis=analysis,
                )
                self.session.commit()
                created += 1
            except Exception:
                self.session.rollback()
                self.storage.delete(image_path)
                raise
        return created

    def reset(self) -> int:
        demo_rows = self.repository.demo_observations()
        staged = [self.storage.stage_delete(item.image_path) for item in demo_rows]
        try:
            for item in demo_rows:
                self.repository.delete(item)
            self.session.commit()
        except Exception:
            self.session.rollback()
            for item in staged:
                self.storage.restore_delete(item)
            raise
        for item in staged:
            self.storage.finalize_delete(item)
        return len(demo_rows)

    @staticmethod
    def _summary(scene: DemoScene) -> str:
        counts: dict[str, int] = {}
        for item in scene.objects:
            counts[item.display_name] = counts.get(item.display_name, 0) + 1
        details = "、".join(f"{name} {count} 个" for name, count in counts.items())
        return f"演示观察：检测到 {len(scene.objects)} 个物体（{details}）。"

    @staticmethod
    def _render_scene(scene: DemoScene) -> bytes:
        image = Image.new("RGB", (960, 640), "#d9e9e3")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 430, 960, 640), fill="#9b8067")
        palette = ("#33b98c", "#4267d5", "#e38b4c", "#9a5bd5", "#d45468")
        for index, item in enumerate(scene.objects):
            x1, y1, x2, y2 = item.bbox
            box = (int(x1 * 960), int(y1 * 640), int(x2 * 960), int(y2 * 640))
            color = palette[index % len(palette)]
            draw.rounded_rectangle(box, radius=14, fill=color, outline="#ffffff", width=4)
            draw.text((box[0] + 8, box[1] + 8), item.label, fill="#ffffff")
        output = BytesIO()
        image.save(output, format="PNG", optimize=True)
        return output.getvalue()
