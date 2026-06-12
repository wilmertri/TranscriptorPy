import json
import subprocess
from pathlib import Path

from transcriptorpy.metadata_archivo import ErrorLecturaMetadata, MetadataAudio, PuertoMetadata


class MetadataFfprobe:
    def obtener_metadata(self, ruta: str) -> MetadataAudio:
        try:
            tamano_bytes = Path(ruta).stat().st_size
        except OSError as exc:
            raise ErrorLecturaMetadata(ruta) from exc

        try:
            proc = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", ruta],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise ErrorLecturaMetadata("ffprobe no encontrado en el sistema") from exc

        if proc.returncode != 0:
            raise ErrorLecturaMetadata(ruta)

        try:
            datos = json.loads(proc.stdout)
            duracion_segundos = float(datos["format"]["duration"])
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            raise ErrorLecturaMetadata(ruta) from exc

        return MetadataAudio(tamano_bytes=tamano_bytes, duracion_segundos=duracion_segundos)
