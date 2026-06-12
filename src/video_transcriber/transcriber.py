from __future__ import annotations

from pathlib import Path

from video_transcriber.models import TranscriptResult, TranscriptSegment


class VideoTranscriptionService:
    def __init__(
        self,
        model_name: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "No se pudo importar 'faster-whisper'. Ejecuta 'pip install -e .[dev]' o 'pip install -e .'."
                ) from exc

            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(
        self,
        source_file: str | Path,
        language: str | None = None,
        task: str = "transcribe",
        beam_size: int = 5,
        vad_filter: bool = True,
    ) -> TranscriptResult:
        source_path = Path(source_file).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"No existe el archivo: {source_path}")

        try:
            segments, info = self._transcribe_once(
                source_path=source_path,
                language=language,
                task=task,
                beam_size=beam_size,
                vad_filter=vad_filter,
            )
        except RuntimeError as exc:
            message = str(exc).lower()
            if self.device == "auto" and any(token in message for token in ("cublas", "cudnn", "cuda")):
                self.device = "cpu"
                self._model = None
                segments, info = self._transcribe_once(
                    source_path=source_path,
                    language=language,
                    task=task,
                    beam_size=beam_size,
                    vad_filter=vad_filter,
                )
            else:
                raise

        collected_segments = [
            TranscriptSegment(
                start_seconds=segment.start,
                end_seconds=segment.end,
                text=segment.text.strip(),
            )
            for segment in segments
        ]

        return TranscriptResult(
            source_file=source_path,
            detected_language=getattr(info, "language", language),
            duration_seconds=getattr(info, "duration", None),
            segments=collected_segments,
        )

    def _transcribe_once(
        self,
        source_path: Path,
        language: str | None,
        task: str,
        beam_size: int,
        vad_filter: bool,
    ):
        model = self._load_model()
        return model.transcribe(
            str(source_path),
            language=language,
            task=task,
            beam_size=beam_size,
            vad_filter=vad_filter,
        )
