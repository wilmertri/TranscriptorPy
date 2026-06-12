from dataclasses import dataclass

from transcriptorpy.metadata_archivo import PuertoMetadata, ErrorLecturaMetadata
from transcriptorpy.motor_transcripcion import MotorTranscripcion, ResultadoTranscripcion
from transcriptorpy.validador_entrada import validar_entrada


@dataclass
class ResultadoProcesamiento:
    exitoso: bool
    transcripcion: ResultadoTranscripcion | None = None
    motivo: str | None = None


def procesar_transcripcion(
    motor: MotorTranscripcion,
    puerto_metadata: PuertoMetadata,
    nombre: str,
) -> ResultadoProcesamiento:
    try:
        metadata = puerto_metadata.obtener_metadata(nombre)
    except ErrorLecturaMetadata:
        return ResultadoProcesamiento(exitoso=False, motivo="ILEGIBLE")
    validacion = validar_entrada(nombre, metadata.tamano_bytes, metadata.duracion_segundos)
    if not validacion.valido:
        return ResultadoProcesamiento(exitoso=False, motivo=validacion.motivo)
    resultado_motor = motor.transcribir(nombre)
    return ResultadoProcesamiento(exitoso=True, transcripcion=resultado_motor)
