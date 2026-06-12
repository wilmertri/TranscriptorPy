from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from video_transcriber.models import TranscriptResult


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_directory(base_dir: Path, source_file: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in source_file.stem)
    return ensure_directory(base_dir / f"{safe_name}_{timestamp}")


def format_timestamp(total_seconds: float) -> str:
    whole_seconds = max(0, int(total_seconds))
    hours, remainder = divmod(whole_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def render_transcript_text(result: TranscriptResult, include_timestamps: bool) -> str:
    if not result.segments:
        return ""

    lines: list[str] = []
    for segment in result.segments:
        cleaned = segment.text.strip()
        if not cleaned:
            continue
        if include_timestamps:
            start = format_timestamp(segment.start_seconds)
            end = format_timestamp(segment.end_seconds)
            lines.append(f"[{start} -> {end}] {cleaned}")
        else:
            lines.append(cleaned)
    return "\n".join(lines).strip()


def save_json_metadata(result: TranscriptResult, destination: Path) -> Path:
    payload = {
        "source_file": str(result.source_file),
        "detected_language": result.detected_language,
        "duration_seconds": result.duration_seconds,
        "segments": [
            {
                "start_seconds": segment.start_seconds,
                "end_seconds": segment.end_seconds,
                "text": segment.text,
            }
            for segment in result.segments
        ],
        "full_text": result.full_text,
    }
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return destination
