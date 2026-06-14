import subprocess

from transcriptorpy.procesador_audio import ErrorProcesamientoAudio


class AudioFfmpeg:
    def extraer_audio(self, ruta_entrada: str, ruta_salida: str) -> None:
        self._ejecutar_ffmpeg(
            [
                "ffmpeg", "-y", "-i", ruta_entrada,
                "-ac", "1", "-ar", "16000",
                ruta_salida,
            ],
            ruta_entrada,
        )

    def recortar(
        self,
        ruta_entrada: str,
        ruta_salida: str,
        inicio_segundos: float,
        duracion_segundos: float,
    ) -> None:
        # -ss después de -i: seek por muestra (preciso), no por keyframe
        self._ejecutar_ffmpeg(
            [
                "ffmpeg", "-y", "-i", ruta_entrada,
                "-ss", str(inicio_segundos),
                "-t", str(duracion_segundos),
                "-ac", "1", "-ar", "16000",
                ruta_salida,
            ],
            ruta_entrada,
        )

    def _ejecutar_ffmpeg(self, cmd: list[str], ruta_entrada: str) -> None:
        try:
            proc = subprocess.run(cmd, capture_output=True)
        except FileNotFoundError as exc:
            raise ErrorProcesamientoAudio("ffmpeg no encontrado en el sistema") from exc
        if proc.returncode != 0:
            raise ErrorProcesamientoAudio(ruta_entrada)
