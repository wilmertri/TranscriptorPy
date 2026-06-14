import subprocess

from transcriptorpy.procesador_audio import ErrorProcesamientoAudio


class AudioFfmpeg:
    def extraer_audio(self, ruta_entrada: str, ruta_salida: str) -> None:
        try:
            proc = subprocess.run(
                [
                    "ffmpeg", "-y", "-i", ruta_entrada,
                    "-ac", "1", "-ar", "16000",
                    ruta_salida,
                ],
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise ErrorProcesamientoAudio("ffmpeg no encontrado en el sistema") from exc
        if proc.returncode != 0:
            raise ErrorProcesamientoAudio(ruta_entrada)
