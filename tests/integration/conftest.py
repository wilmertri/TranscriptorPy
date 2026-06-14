import shutil
import subprocess

import pytest


def _binario_disponible(nombre: str) -> bool:
    return shutil.which(nombre) is not None


@pytest.fixture
def audio_prueba(tmp_path):
    if not _binario_disponible("ffmpeg"):
        pytest.skip("ffmpeg no disponible en este sistema")
    if not _binario_disponible("ffprobe"):
        pytest.skip("ffprobe no disponible en este sistema")
    ruta = tmp_path / "prueba.wav"
    subprocess.run(
        [
            "ffmpeg", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=2",
            "-y", str(ruta),
        ],
        check=True,
        capture_output=True,
    )
    return ruta


@pytest.fixture
def archivo_invalido(tmp_path):
    if not _binario_disponible("ffprobe"):
        pytest.skip("ffprobe no disponible en este sistema")
    ruta = tmp_path / "basura.mp4"
    ruta.write_bytes(b"esto no es un archivo de audio valido")
    return ruta


@pytest.fixture
def media_con_audio(tmp_path):
    if not _binario_disponible("ffmpeg"):
        pytest.skip("ffmpeg no disponible en este sistema")
    ruta = tmp_path / "entrada.mp4"
    subprocess.run(
        [
            "ffmpeg", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=2",
            "-y", str(ruta),
        ],
        check=True,
        capture_output=True,
    )
    return ruta


@pytest.fixture
def archivo_no_media(tmp_path):
    if not _binario_disponible("ffmpeg"):
        pytest.skip("ffmpeg no disponible en este sistema")
    ruta = tmp_path / "basura.mov"
    ruta.write_bytes(b"esto no es un archivo de media valido")
    return ruta
