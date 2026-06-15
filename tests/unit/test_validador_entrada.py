from transcriptorpy.validador_entrada import validar_entrada
from transcriptorpy.motivos import MotivoRechazo
from transcriptorpy.tamano_archivo import LIMITE_BYTES
from transcriptorpy.duracion_archivo import LIMITE_SEGUNDOS


def test_entrada_valida_devuelve_resultado_valido():
    resultado = validar_entrada("audio.mp3", 500 * 1024 * 1024, 1800)
    assert resultado.valido is True
    assert resultado.motivo is None


def test_formato_no_soportado_devuelve_motivo_formato():
    resultado = validar_entrada("video.avi", 500 * 1024 * 1024, 1800)
    assert resultado.valido is False
    assert resultado.motivo == MotivoRechazo.FORMATO


def test_tamano_excedido_devuelve_motivo_tamano():
    resultado = validar_entrada("audio.mp3", LIMITE_BYTES + 1, 1800)
    assert resultado.valido is False
    assert resultado.motivo == MotivoRechazo.TAMANO


def test_duracion_excedida_devuelve_motivo_duracion():
    resultado = validar_entrada("audio.mp3", 500 * 1024 * 1024, LIMITE_SEGUNDOS + 1)
    assert resultado.valido is False
    assert resultado.motivo == MotivoRechazo.DURACION


def test_formato_y_tamano_invalidos_reporta_formato_primero():
    resultado = validar_entrada("video.avi", LIMITE_BYTES + 1, 1800)
    assert resultado.valido is False
    assert resultado.motivo == MotivoRechazo.FORMATO
