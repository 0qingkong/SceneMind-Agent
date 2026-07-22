from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from dataclasses import dataclass


class ImageStorageError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class StagedDelete:
    original: Path
    staged: Path


class ImageStorage:
    _EXTENSIONS = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()

    def save(self, content: bytes, mime_type: str) -> str:
        extension = self._EXTENSIONS.get(mime_type)
        if extension is None:
            raise ImageStorageError(f"Unsupported image MIME type: {mime_type}")
        self.root.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}{extension}"
        destination = self.root / filename
        temporary = self.root / f".{filename}.tmp"
        try:
            temporary.write_bytes(content)
            temporary.replace(destination)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            raise ImageStorageError(f"Unable to save scene image: {exc}") from exc
        return filename

    def resolve(self, relative_path: str) -> Path:
        if not relative_path or Path(relative_path).is_absolute():
            raise ImageStorageError("Invalid stored image path")
        candidate = (self.root / relative_path).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as exc:
            raise ImageStorageError("Stored image path escapes storage root") from exc
        return candidate

    def existing_path(self, relative_path: str) -> Path | None:
        candidate = self.resolve(relative_path)
        return candidate if candidate.is_file() else None

    def delete(self, relative_path: str) -> None:
        try:
            self.resolve(relative_path).unlink(missing_ok=True)
        except OSError as exc:
            raise ImageStorageError(f"Unable to delete scene image: {exc}") from exc

    def stage_delete(self, relative_path: str) -> StagedDelete | None:
        original = self.resolve(relative_path)
        if not original.exists():
            return None
        staged = self.root / f".{original.name}.{uuid4().hex}.delete"
        try:
            original.replace(staged)
        except OSError as exc:
            raise ImageStorageError(f"Unable to stage image deletion: {exc}") from exc
        return StagedDelete(original=original, staged=staged)

    @staticmethod
    def restore_delete(staged_delete: StagedDelete | None) -> None:
        if staged_delete and staged_delete.staged.exists():
            staged_delete.staged.replace(staged_delete.original)

    @staticmethod
    def finalize_delete(staged_delete: StagedDelete | None) -> None:
        if staged_delete:
            staged_delete.staged.unlink(missing_ok=True)
