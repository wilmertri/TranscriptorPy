import shutil
from pathlib import Path

import pytest

from transcriptorpy.fuente_contenido import ErrorObtencionContenido

pytestmark = [pytest.mark.integration, pytest.mark.network]

_URL_ESTABLE = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
_URL_INEXISTENTE = "https://www.youtube.com/watch?v=000000noexiste0"


@pytest.fixture(autouse=True)
def requiere_ytdlp():
    pytest.importorskip("yt_dlp", reason="yt-dlp no instalado")


def test_descarga_audio_youtube_camino_feliz(tmp_path):
    from transcriptorpy.fuente_youtube_ytdlp import FuenteYoutubeYtdlp

    if not shutil.which("ffprobe"):
        pytest.skip("ffprobe no disponible (necesario para verificar duración)")

    destino = str(tmp_path / "descargado")
    try:
        FuenteYoutubeYtdlp().obtener(_URL_ESTABLE, destino)
    except ErrorObtencionContenido as exc:
        pytest.skip(f"no hay red o el video no es accesible: {exc}")

    assert Path(destino).exists()
    assert Path(destino).stat().st_size > 0

    from transcriptorpy.metadata_ffprobe import MetadataFfprobe
    metadata = MetadataFfprobe().obtener_metadata(destino)
    assert metadata.duracion_segundos > 0
    assert abs(metadata.duracion_segundos - 19) < 5


def test_video_inexistente_lanza_error_obtencion_contenido(tmp_path):
    from transcriptorpy.fuente_youtube_ytdlp import FuenteYoutubeYtdlp

    with pytest.raises(ErrorObtencionContenido):
        FuenteYoutubeYtdlp().obtener(_URL_INEXISTENTE, str(tmp_path / "descargado"))
