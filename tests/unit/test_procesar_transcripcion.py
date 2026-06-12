from transcriptorpy.procesar_transcripcion import procesar_transcripcion
from transcriptorpy.motor_transcripcion import MotorFalso
from transcriptorpy.metadata_archivo import MetadataFalsa

_METADATA_VALIDA = MetadataFalsa(tamano_bytes=500 * 1024 * 1024, duracion_segundos=1800)


def test_entrada_valida_devuelve_resultado_exitoso():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = procesar_transcripcion(
        motor=motor,
        puerto_metadata=_METADATA_VALIDA,
        nombre="audio.mp3",
    )
    assert resultado.exitoso is True
    assert resultado.transcripcion.texto == "hola"
    assert resultado.transcripcion.idioma == "es"


def test_formato_no_soportado_devuelve_rechazo_con_motivo():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = procesar_transcripcion(
        motor=motor,
        puerto_metadata=_METADATA_VALIDA,
        nombre="video.avi",
    )
    assert resultado.exitoso is False
    assert resultado.motivo == "FORMATO"


def test_motor_no_es_invocado_cuando_la_validacion_falla():
    motor = MotorFalso(texto="hola", idioma="es")
    procesar_transcripcion(
        motor=motor,
        puerto_metadata=_METADATA_VALIDA,
        nombre="video.avi",
    )
    assert motor.fue_llamado is False


def test_metadata_ilegible_devuelve_rechazo_ilegible_y_no_llama_al_motor():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = procesar_transcripcion(
        motor=motor,
        puerto_metadata=MetadataFalsa.que_falla(),
        nombre="audio.mp3",
    )
    assert resultado.exitoso is False
    assert resultado.motivo == "ILEGIBLE"
    assert motor.fue_llamado is False
