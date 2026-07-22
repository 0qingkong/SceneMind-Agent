from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Observation(Base):
    __tablename__ = "observations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    image_path: Mapped[str] = mapped_column(String(255), unique=True)
    original_filename: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(50))
    image_width: Mapped[int] = mapped_column(Integer)
    image_height: Mapped[int] = mapped_column(Integer)
    engine: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text)
    object_count: Mapped[int] = mapped_column(Integer)
    relation_count: Mapped[int] = mapped_column(Integer)

    objects: Mapped[list[ObservedObject]] = relationship(
        back_populates="observation",
        cascade="all, delete-orphan",
        order_by="ObservedObject.sort_order",
    )
    relations: Mapped[list[ObservedRelation]] = relationship(
        back_populates="observation",
        cascade="all, delete-orphan",
    )


class ObservedObject(Base):
    __tablename__ = "observed_objects"
    __table_args__ = (
        UniqueConstraint("observation_id", "id", name="uq_object_observation_id"),
    )

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(100))
    observation_id: Mapped[str] = mapped_column(
        ForeignKey("observations.id", ondelete="CASCADE"), index=True
    )
    sort_order: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(100), index=True)
    display_name: Mapped[str] = mapped_column(String(100), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    bbox_x1: Mapped[float] = mapped_column(Float)
    bbox_y1: Mapped[float] = mapped_column(Float)
    bbox_x2: Mapped[float] = mapped_column(Float)
    bbox_y2: Mapped[float] = mapped_column(Float)

    observation: Mapped[Observation] = relationship(back_populates="objects")


class ObservedRelation(Base):
    __tablename__ = "observed_relations"
    __table_args__ = (
        UniqueConstraint("observation_id", "id", name="uq_relation_observation_id"),
    )

    row_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[str] = mapped_column(String(100))
    observation_id: Mapped[str] = mapped_column(
        ForeignKey("observations.id", ondelete="CASCADE"), index=True
    )
    subject_id: Mapped[str] = mapped_column(String(100))
    predicate: Mapped[str] = mapped_column(String(30), index=True)
    object_id: Mapped[str] = mapped_column(String(100))
    score: Mapped[float] = mapped_column(Float)
    method: Mapped[str] = mapped_column(String(30), default="geometry")
    center_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    iou: Mapped[float | None] = mapped_column(Float, nullable=True)
    containment_ratio: Mapped[float | None] = mapped_column(Float, nullable=True)

    observation: Mapped[Observation] = relationship(back_populates="relations")
