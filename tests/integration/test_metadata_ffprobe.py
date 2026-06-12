import pytest

from transcriptorpy.metadata_ffprobe import MetadataFfprobe
from transcriptorpy.metadata_archivo import ErrorLecturaMetadata

pytestmark = pytest.mark.integration


def test_camino_feliz_devuelve_tamano_y_duracion_reales(audio_prueba):
    adaptador = MetadataFfprobe()
    resultado = adaptador.obtener_metadata(str(audio_prueba))
    assert resultado.tamano_bytes > 0
    assert abs(resultado.duracion_segundos - 2.0) < 0.5


def test_archivo_invalido_lanza_error_lectura_metadata(archivo_invalido):
    adaptador = MetadataFfprobe()
    with pytest.raises(ErrorLecturaMetadata):
        adaptador.obtener_metadata(str(archivo_invalido))
