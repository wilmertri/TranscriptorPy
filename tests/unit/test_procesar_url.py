from transcriptorpy.procesar_transcripcion import CasoDeUsoTranscripcion
from transcriptorpy.motor_transcripcion import MotorFalso
from transcriptorpy.metadata_archivo import MetadataFalsa
from transcriptorpy.procesador_audio import AudioFalso
from transcriptorpy.fuente_contenido import FuenteFalsa

_METADATA_VALIDA = MetadataFalsa(tamano_bytes=500 * 1024 * 1024, duracion_segundos=1800)


def _caso(fuente=None, motor=None, audio=None):
    return CasoDeUsoTranscripcion(
        motor=motor or MotorFalso(texto="texto", idioma="es"),
        puerto_metadata=_METADATA_VALIDA,
        puerto_audio=audio or AudioFalso(),
        puerto_fuente=fuente or FuenteFalsa(),
    )


def test_url_youtube_descarga_y_transcribe_devolviendo_exito():
    fuente = FuenteFalsa()
    motor = MotorFalso(texto="transcripción", idioma="es")
    audio = AudioFalso()
    resultado = _caso(fuente=fuente, motor=motor, audio=audio).procesar_url(
        "https://www.youtube.com/watch?v=abc123"
    )
    assert resultado.exitoso is True
    assert resultado.transcripcion.texto == "transcripción"
    assert fuente.fue_llamado is True
    assert motor.ruta_recibida != "https://www.youtube.com/watch?v=abc123"


def test_fallo_al_obtener_contenido_devuelve_rechazo_fuente_y_motor_no_llamado():
    fuente = FuenteFalsa(debe_fallar=True)
    motor = MotorFalso(texto="x", idioma="es")
    resultado = _caso(fuente=fuente, motor=motor).procesar_url(
        "https://www.youtube.com/watch?v=abc123"
    )
    assert resultado.exitoso is False
    assert resultado.motivo == "FUENTE"
    assert motor.fue_llamado is False


def test_url_no_youtube_devuelve_rechazo_url_invalida_sin_llamar_fuente_ni_motor():
    fuente = FuenteFalsa()
    motor = MotorFalso(texto="x", idioma="es")
    resultado = _caso(fuente=fuente, motor=motor).procesar_url("https://vimeo.com/12345")
    assert resultado.exitoso is False
    assert resultado.motivo == "URL_INVALIDA"
    assert fuente.fue_llamado is False
    assert motor.fue_llamado is False
