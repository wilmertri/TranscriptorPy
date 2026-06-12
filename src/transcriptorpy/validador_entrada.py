from dataclasses import dataclass

from transcriptorpy.formato_archivo import validar_formato
from transcriptorpy.tamano_archivo import validar_tamano
from transcriptorpy.duracion_archivo import validar_duracion


@dataclass
class ResultadoValidacion:
    valido: bool
    motivo: str | None = None


def validar_entrada(nombre: str, tamano_bytes: int, duracion_segundos: float) -> ResultadoValidacion:
    if not validar_formato(nombre):
        return ResultadoValidacion(valido=False, motivo="FORMATO")
    if not validar_tamano(tamano_bytes):
        return ResultadoValidacion(valido=False, motivo="TAMANO")
    if not validar_duracion(duracion_segundos):
        return ResultadoValidacion(valido=False, motivo="DURACION")
    return ResultadoValidacion(valido=True)
