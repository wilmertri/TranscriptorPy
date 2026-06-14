import os
from pathlib import Path

import openai
import pytest

from transcriptorpy.motor_openai import MotorOpenAI

pytestmark = [pytest.mark.integration, pytest.mark.network]

_AUDIO_FIXTURE = Path(__file__).parent.parent / "fixtures" / "audio_es.wav"


@pytest.fixture
def cliente_openai(ssl_context_local):
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("requiere OPENAI_API_KEY")
    if ssl_context_local is not None:
        import httpx
        return openai.OpenAI(http_client=httpx.Client(verify=ssl_context_local))
    return openai.OpenAI()


def test_transcripcion_real_devuelve_texto_con_palabra_esperada(cliente_openai):
    if not _AUDIO_FIXTURE.exists():
        pytest.skip(f"fixture de audio no encontrado: {_AUDIO_FIXTURE}")
    motor = MotorOpenAI(cliente=cliente_openai)
    resultado = motor.transcribir(str(_AUDIO_FIXTURE))
    assert len(resultado.texto.strip()) > 0
    assert "hola" in resultado.texto.lower()
    assert resultado.idioma is None
