from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from video_transcriber.exporters import TranscriptExporter
from video_transcriber.transcriber import VideoTranscriptionService
from video_transcriber.utils import build_output_directory, ensure_directory, save_json_metadata

try:
    from fastapi import FastAPI, File, Form, UploadFile
except ImportError as exc:
    raise RuntimeError("Instala las dependencias web con 'pip install -e .[web]' para usar la API.") from exc


app = FastAPI(title="Video Transcriber API", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/transcriptions")
async def create_transcription(
    file: UploadFile = File(...),
    language: str | None = Form(default=None),
    model: str = Form(default="small"),
    device: str = Form(default="cpu"),
    compute_type: str = Form(default="int8"),
    task: str = Form(default="transcribe"),
    timestamps: bool = Form(default=False),
    output_formats: str = Form(default="txt"),
    output_dir: str = Form(default="outputs"),
) -> dict[str, object]:
    base_output_dir = ensure_directory(Path(output_dir).expanduser())

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        uploaded_path = temp_dir / (file.filename or "uploaded_media.bin")
        with uploaded_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        service = VideoTranscriptionService(
            model_name=model,
            device=device,
            compute_type=compute_type,
        )
        exporter = TranscriptExporter()
        result = service.transcribe(
            source_file=uploaded_path,
            language=language,
            task=task,
        )

        export_dir = build_output_directory(base_output_dir, Path(file.filename or "uploaded_media"))
        generated_files: list[str] = []
        requested_formats = [item.strip().lower() for item in output_formats.split(",") if item.strip()]
        for output_format in requested_formats:
            destination = export_dir / f"transcript.{output_format}"
            if output_format == "txt":
                exporter.export_txt(result, destination, include_timestamps=timestamps)
                generated_files.append(str(destination))
            elif output_format == "pdf":
                exporter.export_pdf(result, destination, include_timestamps=timestamps)
                generated_files.append(str(destination))
            elif output_format == "docx":
                exporter.export_docx(result, destination, include_timestamps=timestamps)
                generated_files.append(str(destination))

        metadata_path = export_dir / "transcript.json"
        save_json_metadata(result, metadata_path)
        generated_files.append(str(metadata_path))

    return {
        "source_name": file.filename,
        "detected_language": result.detected_language,
        "duration_seconds": result.duration_seconds,
        "files": generated_files,
    }
