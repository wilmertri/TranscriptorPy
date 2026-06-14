from transcriptorpy.fragmentacion import planificar_fragmentos


def test_audio_corto_produce_una_sola_ventana():
    resultado = planificar_fragmentos(duracion_total=600, duracion_maxima=1200)
    assert resultado == [(0, 600)]


def test_audio_largo_produce_n_ventanas_iguales_exactas():
    resultado = planificar_fragmentos(duracion_total=3600, duracion_maxima=1200)
    assert resultado == [(0, 1200), (1200, 1200), (2400, 1200)]


def test_audio_largo_no_multiplo_produce_ventanas_iguales_por_debajo_del_maximo():
    resultado = planificar_fragmentos(duracion_total=3000, duracion_maxima=1200)
    assert resultado == [(0, 1000), (1000, 1000), (2000, 1000)]


def test_duracion_exactamente_igual_al_maximo_produce_una_sola_ventana():
    resultado = planificar_fragmentos(duracion_total=1200, duracion_maxima=1200)
    assert resultado == [(0, 1200)]
