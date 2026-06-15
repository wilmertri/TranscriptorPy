import tempfile
from dataclasses import dataclass
from pathlib import Path

from transcriptorpy.formato_archivo import es_video
from transcriptorpy.fuente_contenido import PuertoFuenteContenido, ErrorObtencionContenido
from transcriptorpy.metadata_archivo import PuertoMetadata, ErrorLecturaMetadata
from transcriptorpy.motivos import MotivoRechazo
from transcriptorpy.motor_transcripcion import MotorTranscripcion, ResultadoTranscripcion, ErrorTranscripcion
from transcriptorpy.procesador_audio import PuertoAudio, ErrorProcesamientoAudio
from transcriptorpy.url_youtube import es_url_youtube
from transcriptorpy.validador_entrada import validar_entrada


@dataclass
class ResultadoProcesamiento:
    exitoso: bool
    transcripcion: ResultadoTranscripcion | None = None
    motivo: MotivoRechazo | None = None


class CasoDeUsoTranscripcion:
    def __init__(
        self,
        motor: MotorTranscripcion,
        puerto_metadata: PuertoMetadata,
        puerto_audio: PuertoAudio,
        puerto_fuente: PuertoFuenteContenido,
    ) -> None:
        self._motor = motor
        self._puerto_metadata = puerto_metadata
        self._puerto_audio = puerto_audio
        self._puerto_fuente = puerto_fuente

    def procesar_archivo(self, nombre: str) -> ResultadoProcesamiento:
        return self._procesar_local(nombre)

    def procesar_url(self, url: str) -> ResultadoProcesamiento:
        if not es_url_youtube(url):
            return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.URL_INVALIDA)
        with tempfile.TemporaryDirectory() as tmp_dir:
            destino = str(Path(tmp_dir) / "contenido.mp4")
            try:
                self._puerto_fuente.obtener(url, destino)
            except ErrorObtencionContenido:
                return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.FUENTE)
            return self._procesar_local(destino)

    def _procesar_local(self, ruta: str) -> ResultadoProcesamiento:
        try:
            metadata = self._puerto_metadata.obtener_metadata(ruta)
        except ErrorLecturaMetadata:
            return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.ILEGIBLE)
        validacion = validar_entrada(ruta, metadata.tamano_bytes, metadata.duracion_segundos)
        if not validacion.valido:
            return ResultadoProcesamiento(exitoso=False, motivo=validacion.motivo)
        if es_video(ruta):
            with tempfile.TemporaryDirectory() as directorio_temporal:
                ruta_audio = str(Path(directorio_temporal) / "audio.wav")
                try:
                    self._puerto_audio.extraer_audio(ruta, ruta_audio)
                except ErrorProcesamientoAudio:
                    return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.EXTRACCION)
                try:
                    resultado_motor = self._motor.transcribir(ruta_audio)
                except ErrorTranscripcion:
                    return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.MOTOR)
        else:
            try:
                resultado_motor = self._motor.transcribir(ruta)
            except ErrorTranscripcion:
                return ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.MOTOR)
        return ResultadoProcesamiento(exitoso=True, transcripcion=resultado_motor)
