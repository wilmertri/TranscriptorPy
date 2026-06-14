import pytest

from transcriptorpy.audio_ffmpeg import AudioFfmpeg
from transcriptorpy.metadata_ffprobe import MetadataFfprobe
from transcriptorpy.procesador_audio import ErrorProcesamientoAudio

pytestmark = pytest.mark.integration


def test_camino_feliz_extrae_audio_a_wav(media_con_audio, tmp_path):
    ruta_salida = tmp_path / "audio_extraido.wav"
    adaptador = AudioFfmpeg()
    adaptador.extraer_audio(str(media_con_audio), str(ruta_salida))
    assert ruta_salida.exists()
    metadata = MetadataFfprobe()
    resultado = metadata.obtener_metadata(str(ruta_salida))
    assert resultado.tamano_bytes > 0
    assert resultado.duracion_segundos > 0


def test_entrada_invalida_lanza_error_procesamiento_audio(archivo_no_media, tmp_path):
    ruta_salida = tmp_path / "salida.wav"
    adaptador = AudioFfmpeg()
    with pytest.raises(ErrorProcesamientoAudio):
        adaptador.extraer_audio(str(archivo_no_media), str(ruta_salida))
