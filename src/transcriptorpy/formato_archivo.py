from pathlib import Path

_FORMATOS_SOPORTADOS = {".mp3", ".wav", ".m4a", ".mp4", ".mov"}
_FORMATOS_VIDEO = {".mp4", ".mov"}


def validar_formato(nombre: str) -> bool:
    return Path(nombre).suffix.lower() in _FORMATOS_SOPORTADOS


def es_video(nombre: str) -> bool:
    return Path(nombre).suffix.lower() in _FORMATOS_VIDEO
