from dataclasses import dataclass
from typing import Protocol


@dataclass
class ResultadoTranscripcion:
    texto: str
    idioma: str


class MotorTranscripcion(Protocol):
    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        ...


class MotorFalso:
    def __init__(self, texto: str, idioma: str) -> None:
        self._texto = texto
        self._idioma = idioma
        self.fue_llamado = False

    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        self.fue_llamado = True
        return ResultadoTranscripcion(texto=self._texto, idioma=self._idioma)
