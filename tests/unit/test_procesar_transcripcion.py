from pathlib import Path

from transcriptorpy.procesar_transcripcion import CasoDeUsoTranscripcion
from transcriptorpy.motor_transcripcion import MotorFalso
from transcriptorpy.metadata_archivo import MetadataFalsa
from transcriptorpy.motivos import MotivoRechazo
from transcriptorpy.procesador_audio import AudioFalso
from transcriptorpy.fuente_contenido import FuenteFalsa

_METADATA_VALIDA = MetadataFalsa(tamano_bytes=500 * 1024 * 1024, duracion_segundos=1800)


def _caso(motor, audio=None, metadata=None):
    return CasoDeUsoTranscripcion(
        motor=motor,
        puerto_metadata=metadata or _METADATA_VALIDA,
        puerto_audio=audio or AudioFalso(),
        puerto_fuente=FuenteFalsa(),
    )


def test_entrada_valida_devuelve_resultado_exitoso():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = _caso(motor).procesar_archivo("audio.mp3")
    assert resultado.exitoso is True
    assert resultado.transcripcion.texto == "hola"
    assert resultado.transcripcion.idioma == "es"


def test_formato_no_soportado_devuelve_rechazo_con_motivo():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = _caso(motor).procesar_archivo("video.avi")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.FORMATO


def test_motor_no_es_invocado_cuando_la_validacion_falla():
    motor = MotorFalso(texto="hola", idioma="es")
    _caso(motor).procesar_archivo("video.avi")
    assert motor.fue_llamado is False


def test_video_extrae_audio_y_motor_recibe_ruta_temporal():
    motor = MotorFalso(texto="transcripción", idioma="es")
    audio = AudioFalso()
    _caso(motor, audio=audio).procesar_archivo("clip.mp4")
    assert audio.fue_llamado is True
    assert motor.ruta_recibida != "clip.mp4"


def test_archivo_temporal_de_video_se_elimina_al_terminar():
    motor = MotorFalso(texto="texto", idioma="es")
    audio = AudioFalso()
    _caso(motor, audio=audio).procesar_archivo("clip.mp4")
    assert audio.ruta_salida is not None
    assert not Path(audio.ruta_salida).exists()


def test_fallo_de_extraccion_devuelve_rechazo_extraccion_y_motor_no_llamado():
    motor = MotorFalso(texto="texto", idioma="es")
    resultado = _caso(motor, audio=AudioFalso.que_falla()).procesar_archivo("clip.mp4")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.EXTRACCION
    assert motor.fue_llamado is False


def test_fallo_del_motor_en_audio_devuelve_rechazo_motor():
    resultado = _caso(MotorFalso.que_falla()).procesar_archivo("audio.mp3")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.MOTOR


def test_fallo_del_motor_en_video_devuelve_rechazo_motor_y_temporal_limpio():
    audio = AudioFalso()
    resultado = _caso(MotorFalso.que_falla(), audio=audio).procesar_archivo("clip.mp4")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.MOTOR
    assert audio.ruta_salida is not None
    assert not Path(audio.ruta_salida).exists()


def test_metadata_ilegible_devuelve_rechazo_ilegible_y_no_llama_al_motor():
    motor = MotorFalso(texto="hola", idioma="es")
    resultado = _caso(motor, metadata=MetadataFalsa.que_falla()).procesar_archivo("audio.mp3")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.ILEGIBLE
    assert motor.fue_llamado is False


def test_motor_devuelve_texto_sin_voz_reconocible_resulta_en_rechazo_sin_voz():
    motor = MotorFalso(texto="   ", idioma=None)
    resultado = _caso(motor).procesar_archivo("audio.mp3")
    assert resultado.exitoso is False
    assert resultado.motivo == MotivoRechazo.SIN_VOZ
    assert resultado.transcripcion is None
