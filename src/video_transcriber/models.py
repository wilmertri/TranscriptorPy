from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class TranscriptSegment:
    start_seconds: float
    end_seconds: float
    text: str


@dataclass(slots=True)
class TranscriptResult:
    source_file: Path
    detected_language: str | None
    duration_seconds: float | None
    segments: list[TranscriptSegment] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return " ".join(segment.text.strip() for segment in self.segments if segment.text.strip()).strip()
