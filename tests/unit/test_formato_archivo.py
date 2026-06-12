from transcriptorpy.formato_archivo import validar_formato


def test_extension_no_soportada_es_rechazada():
    assert validar_formato("video.avi") is False


def test_extension_soportada_es_aceptada():
    assert validar_formato("audio.mp3") is True


def test_extension_en_mayusculas_es_aceptada():
    assert validar_formato("VIDEO.MP4") is True
