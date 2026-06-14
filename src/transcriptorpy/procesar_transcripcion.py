import tempfile
from dataclasses import dataclass
from pathlib import Path

from transcriptorpy.formato_archivo import es_video
from transcriptorpy.metadata_archivo import PuertoMetadata, ErrorLecturaMetadata
from transcriptorpy.motor_transcripcion import MotorTranscripcion, ResultadoTranscripcion, ErrorTranscripcion
from transcriptorpy.procesador_audio import PuertoAudio, ErrorProcesamientoAudio
from transcriptorpy.validador_entrada import validar_entrada


@dataclass
class ResultadoProcesamiento:
    exitoso: bool
    transcripcion: ResultadoTranscripcion | None = None
    motivo: str | None = None


def procesar_transcripcion(
    motor: MotorTranscripcion,
    puerto_metadata: PuertoMetadata,
    puerto_audio: PuertoAudio,
    nombre: str,
) -> ResultadoProcesamiento:
    try:
        metadata = puerto_metadata.obtener_metadata(nombre)
    except ErrorLecturaMetadata:
        return ResultadoProcesamiento(exitoso=False, motivo="ILEGIBLE")
    validacion = validar_entrada(nombre, metadata.tamano_bytes, metadata.duracion_segundos)
    if not validacion.valido:
        return ResultadoProcesamiento(exitoso=False, motivo=validacion.motivo)
    if es_video(nombre):
        with tempfile.TemporaryDirectory() as directorio_temporal:
            ruta_audio = str(Path(directorio_temporal) / "audio.wav")
            try:
                puerto_audio.extraer_audio(nombre, ruta_audio)
            except ErrorProcesamientoAudio:
                return ResultadoProcesamiento(exitoso=False, motivo="EXTRACCION")
            try:
                resultado_motor = motor.transcribir(ruta_audio)
            except ErrorTranscripcion:
                return ResultadoProcesamiento(exitoso=False, motivo="MOTOR")
    else:
        try:
            resultado_motor = motor.transcribir(nombre)
        except ErrorTranscripcion:
            return ResultadoProcesamiento(exitoso=False, motivo="MOTOR")
    return ResultadoProcesamiento(exitoso=True, transcripcion=resultado_motor)
