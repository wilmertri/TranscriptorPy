from typing import Protocol


class ErrorObtencionContenido(Exception):
    pass


class PuertoFuenteContenido(Protocol):
    def obtener(self, url: str, ruta_destino: str) -> None: ...


class FuenteFalsa:
    def __init__(self, *, debe_fallar: bool = False):
        self.debe_fallar = debe_fallar
        self.fue_llamado = False
        self.url_recibida: str | None = None
        self.destino_recibido: str | None = None

    def obtener(self, url: str, ruta_destino: str) -> None:
        if self.debe_fallar:
            raise ErrorObtencionContenido("descarga simulada fallida")
        self.fue_llamado = True
        self.url_recibida = url
        self.destino_recibido = ruta_destino
        with open(ruta_destino, "wb") as f:
            f.write(b"placeholder")
