from dataclasses import dataclass
from typing import Protocol


@dataclass
class ResultadoTranscripcion:
    texto: str
    idioma: str | None = None


class ErrorTranscripcion(Exception):
    pass


class MotorTranscripcion(Protocol):
    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        ...


class MotorFalso:
    def __init__(self, texto: str, idioma: str, _falla: bool = False) -> None:
        self._texto = texto
        self._idioma = idioma
        self._falla = _falla
        self.fue_llamado = False
        self.ruta_recibida: str | None = None

    @classmethod
    def que_falla(cls) -> "MotorFalso":
        return cls(texto="", idioma="", _falla=True)

    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        self.fue_llamado = True
        self.ruta_recibida = ruta_audio
        if self._falla:
            raise ErrorTranscripcion("motor falló")
        return ResultadoTranscripcion(texto=self._texto, idioma=self._idioma)
