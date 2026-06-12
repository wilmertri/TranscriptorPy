from __future__ import annotations

import argparse
from pathlib import Path

from video_transcriber.exporters import TranscriptExporter
from video_transcriber.transcriber import VideoTranscriptionService
from video_transcriber.utils import build_output_directory, ensure_directory, save_json_metadata


SUPPORTED_EXPORTS = ("txt", "pdf", "docx")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Transcribe un archivo de video o audio y exporta la salida a TXT, PDF o DOCX."
    )
    parser.add_argument("source", help="Ruta del archivo de video o audio.")
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directorio base de salida. Default: outputs",
    )
    parser.add_argument(
        "--format",
        nargs="+",
        default=["txt"],
        choices=SUPPORTED_EXPORTS,
        help="Formato(s) de salida. Default: txt",
    )
    parser.add_argument(
        "--language",
        default=None,
        help="Idioma esperado, por ejemplo: es, en, pt. Si se omite, se detecta automaticamente.",
    )
    parser.add_argument(
        "--model",
        default="small",
        help="Modelo Whisper: tiny, base, small, medium, large-v3. Default: small",
    )
    parser.add_argument(
        "--device",
        default="cpu",
        help="Dispositivo de inferencia: cpu, auto o cuda. Default: cpu",
    )
    parser.add_argument(
        "--compute-type",
        default="int8",
        help="Modo de computo para faster-whisper. Default: int8",
    )
    parser.add_argument(
        "--task",
        default="transcribe",
        choices=("transcribe", "translate"),
        help="Modo: transcribe o translate. Default: transcribe",
    )
    parser.add_argument(
        "--beam-size",
        type=int,
        default=5,
        help="Beam size para la decodificacion. Default: 5",
    )
    parser.add_argument(
        "--timestamps",
        action="store_true",
        help="Incluye marcas de tiempo en la salida.",
    )
    parser.add_argument(
        "--disable-vad",
        action="store_true",
        help="Desactiva el filtro VAD.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    source_path = Path(args.source).expanduser()
    if not source_path.exists():
        parser.error(f"No existe el archivo: {source_path}")

    output_base = ensure_directory(Path(args.output_dir).expanduser())
    output_dir = build_output_directory(output_base, source_path)

    service = VideoTranscriptionService(
        model_name=args.model,
        device=args.device,
        compute_type=args.compute_type,
    )
    exporter = TranscriptExporter()

    result = service.transcribe(
        source_file=source_path,
        language=args.language,
        task=args.task,
        beam_size=args.beam_size,
        vad_filter=not args.disable_vad,
    )

    generated_files: list[Path] = []
    for output_format in args.format:
        destination = output_dir / f"transcript.{output_format}"
        if output_format == "txt":
            generated_files.append(exporter.export_txt(result, destination, include_timestamps=args.timestamps))
        elif output_format == "pdf":
            generated_files.append(exporter.export_pdf(result, destination, include_timestamps=args.timestamps))
        elif output_format == "docx":
            generated_files.append(exporter.export_docx(result, destination, include_timestamps=args.timestamps))

    metadata_path = output_dir / "transcript.json"
    save_json_metadata(result, metadata_path)
    generated_files.append(metadata_path)

    print(f"Archivo procesado: {result.source_file}")
    print(f"Idioma detectado: {result.detected_language or 'desconocido'}")
    print(f"Carpeta de salida: {output_dir}")
    for file_path in generated_files:
        print(f"Generado: {file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
