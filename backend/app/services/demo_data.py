from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from io import BytesIO

from PIL import Image, ImageDraw
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import CaptureSession, Observation
from app.repositories.observations import ObservationRepository
from app.schemas.analyze import (
    AnalyzeResponse,
    DetectedObject,
    DetectedRelation,
    RelationEvidence,
)
from app.services.image_storage import ImageStorage, StagedDelete

DEMO_ENGINE = "demo-seed"
DEMO_SESSION_ID = "00000000-0000-4000-8000-000000000201"
DEMO_BASE_TIME = datetime(2026, 8, 1, 9, 0, tzinfo=timezone.utc)
DEMO_QUERIES = (
    "我的杯子最后出现在哪里？",
    "杯子出现过哪些地方？",
    "图书馆里的笔记本电脑在哪里？",
)


@dataclass(frozen=True, slots=True)
class DemoScene:
    observation_id: str
    title: str
    location: str
    filename: str
    objects: tuple[DetectedObject, ...]
    relations: tuple[DetectedRelation, ...]
    session_id: str | None = None
    capture_reason: str | None = None


@dataclass(frozen=True, slots=True)
class DemoSeedResult:
    inserted_observations: int
    skipped_observations: int
    inserted_sessions: int
    skipped_sessions: int
    demo_observation_ids: tuple[str, ...]
    demo_session_ids: tuple[str, ...]
    sample_queries: tuple[str, ...] = DEMO_QUERIES

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DemoResetResult:
    removed_observations: int
    removed_sessions: int
    removed_files: int
    stopped_active_sessions: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


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
    *,
    center_distance: float | None = None,
    iou: float | None = None,
) -> DetectedRelation:
    return DetectedRelation(
        id=relation_id,
        subject_id=subject_id,
        predicate=predicate,  # type: ignore[arg-type]
        object_id=object_id,
        score=score,
        evidence=RelationEvidence(
            method="geometry",
            center_distance=center_distance,
            iou=iou,
        ),
    )


DEMO_SCENES = (
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000101",
        title="[演示] 桌面工作区",
        location="共享办公室",
        filename="demo-desk.png",
        objects=(
            _object("cup-1", "cup", "杯子", 0.94, [0.06, 0.48, 0.20, 0.78]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.96, [0.30, 0.24, 0.69, 0.70]),
            _object("book-1", "book", "书", 0.88, [0.65, 0.72, 0.86, 0.86]),
            _object("chair-1", "chair", "椅子", 0.90, [0.76, 0.20, 0.96, 0.82]),
        ),
        relations=(
            _relation("desk-r1", "cup-1", "left_of", "laptop-1", 0.86, center_distance=0.37),
            _relation("desk-r2", "laptop-1", "right_of", "cup-1", 0.86, center_distance=0.37),
            _relation("desk-r3", "book-1", "below", "laptop-1", 0.72, center_distance=0.38),
            _relation("desk-r4", "laptop-1", "left_of", "chair-1", 0.69, center_distance=0.46),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000102",
        title="[演示] 智慧教室",
        location="教学楼 201",
        filename="demo-classroom.png",
        objects=(
            _object("person-1", "person", "人", 0.96, [0.06, 0.16, 0.24, 0.80]),
            _object("person-2", "person", "人", 0.93, [0.31, 0.18, 0.49, 0.81]),
            _object("chair-1", "chair", "椅子", 0.90, [0.04, 0.60, 0.27, 0.94]),
            _object("bench-1", "bench", "长椅", 0.87, [0.29, 0.61, 0.63, 0.94]),
            _object("plant-1", "potted plant", "盆栽", 0.89, [0.74, 0.30, 0.92, 0.86]),
        ),
        relations=(
            _relation("class-r1", "person-1", "left_of", "person-2", 0.82, center_distance=0.25),
            _relation("class-r2", "person-2", "right_of", "person-1", 0.82, center_distance=0.25),
            _relation("class-r3", "person-2", "left_of", "plant-1", 0.70, center_distance=0.47),
            _relation("class-r4", "person-1", "overlaps", "chair-1", 0.63, iou=0.18),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000103",
        title="[演示] 图书馆阅读区",
        location="图书馆",
        filename="demo-library.png",
        objects=(
            _object("person-1", "person", "人", 0.95, [0.08, 0.14, 0.30, 0.86]),
            _object("book-1", "book", "书", 0.92, [0.38, 0.50, 0.54, 0.65]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.94, [0.55, 0.31, 0.79, 0.66]),
            _object("bottle-1", "bottle", "瓶子", 0.89, [0.84, 0.35, 0.91, 0.68]),
        ),
        relations=(
            _relation("library-r1", "person-1", "left_of", "book-1", 0.79, center_distance=0.34),
            _relation("library-r2", "book-1", "left_of", "laptop-1", 0.76, center_distance=0.23),
            _relation("library-r3", "laptop-1", "left_of", "bottle-1", 0.68, center_distance=0.23),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000104",
        title="[演示] 会话首帧：桌面",
        location="比赛演示台",
        filename="demo-session-first.png",
        session_id=DEMO_SESSION_ID,
        capture_reason="first_valid_sample",
        objects=(
            _object("cup-1", "cup", "杯子", 0.95, [0.12, 0.46, 0.27, 0.77]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.96, [0.43, 0.26, 0.81, 0.70]),
        ),
        relations=(
            _relation("session-r1", "cup-1", "left_of", "laptop-1", 0.84, center_distance=0.43),
            _relation("session-r2", "laptop-1", "right_of", "cup-1", 0.84, center_distance=0.43),
        ),
    ),
    DemoScene(
        observation_id="00000000-0000-4000-8000-000000000105",
        title="[演示] 会话变化：新增书本",
        location="比赛演示台",
        filename="demo-session-change.png",
        session_id=DEMO_SESSION_ID,
        capture_reason="label_multiset_changed",
        objects=(
            _object("cup-1", "cup", "杯子", 0.95, [0.12, 0.46, 0.27, 0.77]),
            _object("book-1", "book", "书", 0.91, [0.30, 0.69, 0.48, 0.82]),
            _object("laptop-1", "laptop", "笔记本电脑", 0.96, [0.50, 0.26, 0.84, 0.70]),
        ),
        relations=(
            _relation("change-r1", "cup-1", "left_of", "laptop-1", 0.83, center_distance=0.47),
            _relation("change-r2", "book-1", "below", "laptop-1", 0.71, center_distance=0.35),
        ),
    ),
)


class DemoDataService:
    def __init__(self, session: Session, storage: ImageStorage) -> None:
        self.session = session
        self.storage = storage
        self.repository = ObservationRepository(session)

    def seed(self) -> DemoSeedResult:
        inserted_sessions = 0
        skipped_sessions = 0
        demo_session = self.session.get(CaptureSession, DEMO_SESSION_ID)
        if demo_session is None:
            demo_session = self._create_session()
            self.session.add(demo_session)
            self.session.commit()
            inserted_sessions = 1
        else:
            skipped_sessions = 1
            if not demo_session.is_demo:
                demo_session = None

        inserted_observations = 0
        skipped_observations = 0
        for index, scene in enumerate(DEMO_SCENES):
            if self.repository.get(scene.observation_id) is not None:
                skipped_observations += 1
                continue
            image_bytes = self._render_scene(scene)
            image_path = self.storage.save(image_bytes, "image/png")
            analysis = AnalyzeResponse(
                trace_id=f"demo-{scene.observation_id}",
                engine=DEMO_ENGINE,
                filename=scene.filename,
                image_width=960,
                image_height=640,
                scene_summary=self._summary(scene),
                objects=list(scene.objects),
                relations=list(scene.relations),
                latency_ms=0,
            )
            session_id = scene.session_id if scene.session_id and demo_session else None
            try:
                self.repository.create(
                    observation_id=scene.observation_id,
                    title=scene.title,
                    location=scene.location,
                    created_at=DEMO_BASE_TIME + timedelta(minutes=index * 10),
                    image_path=image_path,
                    mime_type="image/png",
                    analysis=analysis,
                    source_type="demo_seed" if not session_id else "browser_camera",
                    source_device_id="demo-camera-1" if session_id else None,
                    source_device_name="[演示] Browser Camera" if session_id else "[演示] Seeded Evidence",
                    captured_at=DEMO_BASE_TIME + timedelta(minutes=index * 10),
                    session_id=session_id,
                    is_demo=True,
                    capture_reason=scene.capture_reason,
                )
                self.session.commit()
                inserted_observations += 1
            except Exception:
                self.session.rollback()
                self.storage.delete(image_path)
                raise

        if demo_session is not None:
            saved_count = int(
                self.session.scalar(
                    select(func.count())
                    .select_from(Observation)
                    .where(Observation.session_id == DEMO_SESSION_ID, Observation.is_demo.is_(True))
                )
                or 0
            )
            demo_session.saved_observations = saved_count
            self.session.commit()

        return DemoSeedResult(
            inserted_observations=inserted_observations,
            skipped_observations=skipped_observations,
            inserted_sessions=inserted_sessions,
            skipped_sessions=skipped_sessions,
            demo_observation_ids=tuple(scene.observation_id for scene in DEMO_SCENES),
            demo_session_ids=(DEMO_SESSION_ID,),
        )

    def reset(self) -> DemoResetResult:
        demo_rows = self.repository.demo_observations()
        demo_sessions = list(
            self.session.scalars(
                select(CaptureSession)
                .where(CaptureSession.is_demo.is_(True))
                .options(selectinload(CaptureSession.observations))
            )
        )
        stopped_active = 0
        now = datetime.now(timezone.utc)
        for capture_session in demo_sessions:
            if capture_session.status == "active":
                capture_session.status = "stopped"
                capture_session.ended_at = now
                stopped_active += 1

        staged: list[StagedDelete | None] = []
        try:
            for item in demo_rows:
                staged.append(self.storage.stage_delete(item.image_path))
            demo_ids = {item.id for item in demo_rows}
            for capture_session in demo_sessions:
                for observation in capture_session.observations:
                    if observation.id not in demo_ids:
                        observation.session_id = None
            for item in demo_rows:
                self.repository.delete(item)
            for capture_session in demo_sessions:
                self.session.delete(capture_session)
            self.session.commit()
        except Exception:
            self.session.rollback()
            for item in staged:
                self.storage.restore_delete(item)
            raise
        for item in staged:
            self.storage.finalize_delete(item)
        return DemoResetResult(
            removed_observations=len(demo_rows),
            removed_sessions=len(demo_sessions),
            removed_files=sum(item is not None for item in staged),
            stopped_active_sessions=stopped_active,
        )

    def present(self) -> bool:
        return bool(
            self.session.scalar(
                select(func.count())
                .select_from(Observation)
                .where(or_(Observation.is_demo.is_(True), Observation.engine == DEMO_ENGINE))
            )
        )

    @staticmethod
    def _create_session() -> CaptureSession:
        return CaptureSession(
            id=DEMO_SESSION_ID,
            title="[演示] 低频桌面观察",
            location="比赛演示台",
            source_type="browser_camera",
            device_name="[演示] Browser Camera",
            status="stopped",
            started_at=DEMO_BASE_TIME + timedelta(minutes=25),
            ended_at=DEMO_BASE_TIME + timedelta(minutes=50),
            sample_interval_seconds=5,
            sampled_frames=3,
            analyzed_frames=3,
            saved_observations=2,
            target_query="书",
            last_error=None,
            auto_save_mode="meaningful-change",
            last_labels_json=json.dumps(["book", "cup", "laptop"]),
            target_seen=True,
            last_sampled_at=DEMO_BASE_TIME + timedelta(minutes=50),
            last_saved_at=DEMO_BASE_TIME + timedelta(minutes=50),
            is_demo=True,
        )

    @staticmethod
    def _summary(scene: DemoScene) -> str:
        counts: dict[str, int] = {}
        for item in scene.objects:
            counts[item.display_name] = counts.get(item.display_name, 0) + 1
        details = "、".join(f"{name} {count} 个" for name, count in counts.items())
        reason = f"；保存原因：{scene.capture_reason}" if scene.capture_reason else ""
        return f"演示观察：检测到 {len(scene.objects)} 个物体（{details}）{reason}。"

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
