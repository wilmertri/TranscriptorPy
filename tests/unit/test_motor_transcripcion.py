from transcriptorpy.motor_transcripcion import MotorFalso, MotorTranscripcion


def test_motor_falso_devuelve_texto_e_idioma_configurados():
    motor = MotorFalso(texto="hola mundo", idioma="es")
    resultado = motor.transcribir("audio.wav")
    assert resultado.texto == "hola mundo"
    assert resultado.idioma == "es"


def test_motor_falso_satisface_el_protocolo_del_motor():
    motor: MotorTranscripcion = MotorFalso(texto="prueba", idioma="en")
    resultado = motor.transcribir("ruta/audio.mp3")
    assert resultado.texto == "prueba"
    assert resultado.idioma == "en"
