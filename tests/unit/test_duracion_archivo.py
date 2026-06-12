from transcriptorpy.duracion_archivo import validar_duracion, LIMITE_SEGUNDOS


def test_duracion_mayor_al_limite_es_rechazada():
    assert validar_duracion(LIMITE_SEGUNDOS + 1) is False


def test_duracion_dentro_del_limite_es_aceptada():
    assert validar_duracion(1800) is True


def test_duracion_exactamente_igual_al_limite_es_aceptada():
    assert validar_duracion(LIMITE_SEGUNDOS) is True


def test_duracion_decimal_sobre_el_limite_es_rechazada():
    assert validar_duracion(3600.5) is False
