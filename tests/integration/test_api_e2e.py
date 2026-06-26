import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from transcriptorpy.api import app

pytestmark = [pytest.mark.integration, pytest.mark.network]

_AUDIO_FIXTURE = Path(__file__).parent.parent / "fixtures" / "audio_es.wav"


def test_humo_post_transcripciones_composicion_real():
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("requiere OPENAI_API_KEY")
    if not _AUDIO_FIXTURE.exists():
        pytest.skip(f"fixture de audio no encontrado: {_AUDIO_FIXTURE}")

    cliente = TestClient(app)
    with open(_AUDIO_FIXTURE, "rb") as f:
        respuesta = cliente.post(
            "/transcripciones",
            files={"file": ("audio_es.wav", f, "audio/wav")},
        )

    assert respuesta.status_code == 200
    assert "text/plain" in respuesta.headers["content-type"]
    assert 'filename="transcripcion.txt"' in respuesta.headers["content-disposition"]
    assert len(respuesta.content.decode("utf-8").strip()) > 0
