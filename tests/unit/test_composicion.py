from transcriptorpy.audio_ffmpeg import AudioFfmpeg
from transcriptorpy.composicion import ConfigTranscripcion, construir_caso_de_uso
from transcriptorpy.fuente_youtube_ytdlp import FuenteYoutubeYtdlp
from transcriptorpy.metadata_ffprobe import MetadataFfprobe
from transcriptorpy.motor_con_fragmentacion import MotorConFragmentacion
from transcriptorpy.motor_openai import MotorOpenAI
from transcriptorpy.procesar_transcripcion import CasoDeUsoTranscripcion

_CONFIG = ConfigTranscripcion(openai_api_key="clave-de-prueba-sin-red")


def test_construir_caso_de_uso_devuelve_instancia_correcta():
    assert isinstance(construir_caso_de_uso(_CONFIG), CasoDeUsoTranscripcion)


def test_puerto_metadata_es_metadata_ffprobe():
    caso = construir_caso_de_uso(_CONFIG)
    assert isinstance(caso._puerto_metadata, MetadataFfprobe)


def test_puerto_audio_es_audio_ffmpeg():
    caso = construir_caso_de_uso(_CONFIG)
    assert isinstance(caso._puerto_audio, AudioFfmpeg)


def test_puerto_fuente_es_fuente_youtube_ytdlp():
    caso = construir_caso_de_uso(_CONFIG)
    assert isinstance(caso._puerto_fuente, FuenteYoutubeYtdlp)


def test_motor_es_motor_con_fragmentacion():
    caso = construir_caso_de_uso(_CONFIG)
    assert isinstance(caso._motor, MotorConFragmentacion)


def test_motor_interno_del_decorador_es_motor_openai():
    caso = construir_caso_de_uso(_CONFIG)
    assert isinstance(caso._motor._motor, MotorOpenAI)


def test_metadata_y_audio_son_la_misma_instancia_en_decorador_y_caso_de_uso():
    caso = construir_caso_de_uso(_CONFIG)
    assert caso._puerto_metadata is caso._motor._metadata
    assert caso._puerto_audio is caso._motor._audio
