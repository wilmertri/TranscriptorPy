import os
import shutil
import ssl
import subprocess

import pytest
from dotenv import load_dotenv

load_dotenv()  # carga .env antes de cualquier fixture; no toca el código de producción


def _limpiar_verify_strict(ctx: ssl.SSLContext) -> ssl.SSLContext:
    if hasattr(ssl, "VERIFY_X509_STRICT"):
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
    return ctx


@pytest.fixture(scope="session")
def ssl_context_local():
    """
    Construye un SSLContext usando el bundle indicado en SSL_CERT_FILE (si está en el entorno).
    Necesario cuando un proxy SSL local (e.g. Avast Web Shield) intercepta la conexión
    y re-firma con una CA propia que no cumple RFC 5280 (Basic Constraints no marcado
    como crítico). VERIFY_X509_STRICT se limpia para aceptar esa CA; la verificación de
    cadena completa, hostname y fecha de expiración siguen activas. Retorna None si
    SSL_CERT_FILE no está definido, en cuyo caso el cliente usa los defaults de certifi.
    """
    bundle = os.environ.get("SSL_CERT_FILE")
    if not bundle:
        return None
    return _limpiar_verify_strict(ssl.create_default_context(cafile=bundle))


@pytest.fixture
def relajar_verify_strict(monkeypatch):
    if not os.environ.get("SSL_CERT_FILE"):
        return
    import transcriptorpy.composicion as _composicion
    _original = _composicion.ssl.create_default_context
    def _wrapper(*args, **kwargs):
        return _limpiar_verify_strict(_original(*args, **kwargs))
    monkeypatch.setattr(_composicion.ssl, "create_default_context", _wrapper)


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


@pytest.fixture
def audio_largo(tmp_path):
    if not _binario_disponible("ffmpeg"):
        pytest.skip("ffmpeg no disponible en este sistema")
    if not _binario_disponible("ffprobe"):
        pytest.skip("ffprobe no disponible en este sistema")
    ruta = tmp_path / "largo.wav"
    subprocess.run(
        [
            "ffmpeg", "-f", "lavfi",
            "-i", "sine=frequency=440:duration=5",
            "-y", str(ruta),
        ],
        check=True,
        capture_output=True,
    )
    return ruta
