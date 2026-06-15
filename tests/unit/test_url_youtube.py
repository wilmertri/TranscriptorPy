from transcriptorpy.url_youtube import es_url_youtube


class TestEsUrlYoutube:
    def test_youtube_com_valida(self):
        assert es_url_youtube("https://www.youtube.com/watch?v=abc123") is True

    def test_otra_plataforma(self):
        assert es_url_youtube("https://vimeo.com/12345") is False

    def test_dominio_suplantado(self):
        assert es_url_youtube("https://youtube.com.sitiofalso.ru/x") is False

    def test_youtu_be(self):
        assert es_url_youtube("https://youtu.be/abc123") is True
