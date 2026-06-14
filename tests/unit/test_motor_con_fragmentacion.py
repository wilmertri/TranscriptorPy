from pathlib import Path

from transcriptorpy.motor_con_fragmentacion import MotorConFragmentacion
from transcriptorpy.motor_transcripcion import MotorFalso
from transcriptorpy.metadata_archivo import MetadataFalsa
from transcriptorpy.procesador_audio import AudioFalso


def test_audio_corto_delega_directamente_sin_recortar():
    motor = MotorFalso(texto="solo", idioma="es")
    audio = AudioFalso()
    decorador = MotorConFragmentacion(
        motor_interno=motor,
        puerto_metadata=MetadataFalsa(duracion_segundos=300),
        puerto_audio=audio,
        duracion_maxima=600,
    )
    resultado = decorador.transcribir("audio.wav")
    assert resultado.texto == "solo"
    assert audio.recortes == []


def test_audio_largo_trocea_transcribe_y_concatena():
    motor = MotorFalso(texto="x", idioma="es")
    audio = AudioFalso()
    decorador = MotorConFragmentacion(
        motor_interno=motor,
        puerto_metadata=MetadataFalsa(duracion_segundos=3600),
        puerto_audio=audio,
        duracion_maxima=1200,
    )
    resultado = decorador.transcribir("largo.wav")
    assert len(audio.recortes) == 3
    assert audio.recortes[0][2:] == (0.0, 1200.0)
    assert audio.recortes[1][2:] == (1200.0, 1200.0)
    assert audio.recortes[2][2:] == (2400.0, 1200.0)
    assert resultado.texto == "x x x"
    assert resultado.idioma is None


def test_fragmentos_temporales_se_eliminan_al_terminar():
    audio = AudioFalso()
    decorador = MotorConFragmentacion(
        motor_interno=MotorFalso(texto="x", idioma="es"),
        puerto_metadata=MetadataFalsa(duracion_segundos=3600),
        puerto_audio=audio,
        duracion_maxima=1200,
    )
    decorador.transcribir("largo.wav")
    for _, ruta_salida, _, _ in audio.recortes:
        assert not Path(ruta_salida).exists()
