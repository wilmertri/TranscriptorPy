from transcriptorpy.formato_archivo import validar_formato, es_video


def test_extension_no_soportada_es_rechazada():
    assert validar_formato("video.avi") is False


def test_extension_soportada_es_aceptada():
    assert validar_formato("audio.mp3") is True


def test_extension_en_mayusculas_es_aceptada():
    assert validar_formato("VIDEO.MP4") is True


def test_mp4_es_video():
    assert es_video("clip.mp4") is True


def test_mp3_no_es_video():
    assert es_video("audio.mp3") is False


def test_mov_en_mayusculas_es_video():
    assert es_video("CLIP.MOV") is True
