from pathlib import Path
from typing import Protocol


class ErrorProcesamientoAudio(Exception):
    pass


class PuertoAudio(Protocol):
    def extraer_audio(self, ruta_entrada: str, ruta_salida: str) -> None: ...
    def recortar(self, ruta_entrada: str, ruta_salida: str, inicio_segundos: float, duracion_segundos: float) -> None: ...


class AudioFalso:
    def __init__(self, _falla: bool = False) -> None:
        self.fue_llamado = False
        self.ruta_salida: str | None = None
        self.recortes: list[tuple[str, str, float, float]] = []
        self._falla = _falla

    @classmethod
    def que_falla(cls) -> "AudioFalso":
        return cls(_falla=True)

    def extraer_audio(self, ruta_entrada: str, ruta_salida: str) -> None:
        if self._falla:
            raise ErrorProcesamientoAudio(ruta_entrada)
        self.fue_llamado = True
        self.ruta_salida = ruta_salida
        Path(ruta_salida).write_bytes(b"placeholder")

    def recortar(self, ruta_entrada: str, ruta_salida: str, inicio_segundos: float, duracion_segundos: float) -> None:
        self.recortes.append((ruta_entrada, ruta_salida, inicio_segundos, duracion_segundos))
        Path(ruta_salida).write_bytes(b"placeholder")
