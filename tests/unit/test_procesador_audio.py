from pathlib import Path

import pytest

from transcriptorpy.procesador_audio import AudioFalso, ErrorProcesamientoAudio, PuertoAudio


def test_audio_falso_escribe_placeholder_y_registra_llamada(tmp_path):
    entrada = str(tmp_path / "video.mp4")
    salida = str(tmp_path / "audio.wav")
    puerto = AudioFalso()
    puerto.extraer_audio(entrada, salida)
    assert Path(salida).exists()
    assert puerto.fue_llamado is True


def test_audio_falso_satisface_el_protocolo_del_puerto(tmp_path):
    puerto: PuertoAudio = AudioFalso()
    puerto.extraer_audio(str(tmp_path / "entrada.mp4"), str(tmp_path / "salida.wav"))
    assert Path(tmp_path / "salida.wav").exists()


def test_audio_falso_que_falla_lanza_error_procesamiento_audio(tmp_path):
    puerto = AudioFalso.que_falla()
    with pytest.raises(ErrorProcesamientoAudio):
        puerto.extraer_audio(str(tmp_path / "entrada.mp4"), str(tmp_path / "salida.wav"))
