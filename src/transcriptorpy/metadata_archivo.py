from dataclasses import dataclass
from typing import Protocol


class ErrorLecturaMetadata(Exception):
    pass


@dataclass
class MetadataAudio:
    tamano_bytes: int
    duracion_segundos: float


class PuertoMetadata(Protocol):
    def obtener_metadata(self, ruta: str) -> MetadataAudio:
        ...


class MetadataFalsa:
    def __init__(self, tamano_bytes: int = 0, duracion_segundos: float = 0.0, _falla: bool = False) -> None:
        self._tamano_bytes = tamano_bytes
        self._duracion_segundos = duracion_segundos
        self._falla = _falla

    @classmethod
    def que_falla(cls) -> "MetadataFalsa":
        return cls(_falla=True)

    def obtener_metadata(self, ruta: str) -> MetadataAudio:
        if self._falla:
            raise ErrorLecturaMetadata(ruta)
        return MetadataAudio(
            tamano_bytes=self._tamano_bytes,
            duracion_segundos=self._duracion_segundos,
        )
