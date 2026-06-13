import pytest
import openai
from unittest.mock import MagicMock

from transcriptorpy.motor_openai import MotorOpenAI
from transcriptorpy.motor_transcripcion import ErrorTranscripcion


def test_camino_feliz_devuelve_texto_e_idioma_nulo(tmp_path):
    ruta = tmp_path / "audio.mp3"
    ruta.write_bytes(b"dummy")

    cliente = MagicMock()
    cliente.audio.transcriptions.create.return_value.text = "hola mundo"

    motor = MotorOpenAI(cliente=cliente)
    resultado = motor.transcribir(str(ruta))

    assert resultado.texto == "hola mundo"
    assert resultado.idioma is None


def test_error_de_api_se_relanza_como_error_transcripcion(tmp_path):
    ruta = tmp_path / "audio.mp3"
    ruta.write_bytes(b"dummy")

    cliente = MagicMock()
    cliente.audio.transcriptions.create.side_effect = openai.OpenAIError("fallo de API")

    motor = MotorOpenAI(cliente=cliente)
    with pytest.raises(ErrorTranscripcion):
        motor.transcribir(str(ruta))
