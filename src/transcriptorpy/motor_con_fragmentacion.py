import tempfile
from pathlib import Path

from transcriptorpy.fragmentacion import planificar_fragmentos
from transcriptorpy.metadata_archivo import PuertoMetadata
from transcriptorpy.motor_transcripcion import MotorTranscripcion, ResultadoTranscripcion
from transcriptorpy.procesador_audio import PuertoAudio

# WAV PCM mono 16 kHz ≈ 1.9 MB/min; límite API 25 MB ≈ 13 min; margen conservador
DURACION_MAXIMA_SEGUNDOS = 600.0  # 10 min


class MotorConFragmentacion:
    def __init__(
        self,
        motor_interno: MotorTranscripcion,
        puerto_metadata: PuertoMetadata,
        puerto_audio: PuertoAudio,
        duracion_maxima: float = DURACION_MAXIMA_SEGUNDOS,
    ) -> None:
        self._motor = motor_interno
        self._metadata = puerto_metadata
        self._audio = puerto_audio
        self._duracion_maxima = duracion_maxima

    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        metadata = self._metadata.obtener_metadata(ruta_audio)
        if metadata.duracion_segundos <= self._duracion_maxima:
            return self._motor.transcribir(ruta_audio)
        fragmentos = planificar_fragmentos(metadata.duracion_segundos, self._duracion_maxima)
        textos: list[str] = []
        with tempfile.TemporaryDirectory() as directorio_temporal:
            for i, (inicio, duracion) in enumerate(fragmentos):
                ruta_fragmento = str(Path(directorio_temporal) / f"fragmento_{i}.wav")
                self._audio.recortar(ruta_audio, ruta_fragmento, inicio, duracion)
                resultado = self._motor.transcribir(ruta_fragmento)
                textos.append(resultado.texto)
        return ResultadoTranscripcion(texto=" ".join(textos), idioma=None)
