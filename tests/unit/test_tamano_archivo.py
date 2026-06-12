from transcriptorpy.tamano_archivo import validar_tamano, LIMITE_BYTES


def test_tamano_mayor_al_limite_es_rechazado():
    assert validar_tamano(LIMITE_BYTES + 1) is False


def test_tamano_dentro_del_limite_es_aceptado():
    assert validar_tamano(500 * 1024 * 1024) is True


def test_tamano_exactamente_igual_al_limite_es_aceptado():
    assert validar_tamano(LIMITE_BYTES) is True
