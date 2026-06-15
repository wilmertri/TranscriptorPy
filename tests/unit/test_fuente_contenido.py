import os
import tempfile

import pytest

from transcriptorpy.fuente_contenido import (
    ErrorObtencionContenido,
    FuenteFalsa,
    PuertoFuenteContenido,
)


class TestFuenteFalsa:
    def test_obtener_escribe_placeholder_y_registra_llamada(self):
        fuente = FuenteFalsa()
        with tempfile.TemporaryDirectory() as tmp:
            destino = os.path.join(tmp, "salida.mp4")
            fuente.obtener("https://www.youtube.com/watch?v=abc123", destino)

        assert fuente.fue_llamado is True
        assert fuente.url_recibida == "https://www.youtube.com/watch?v=abc123"
        assert fuente.destino_recibido == destino

    def test_fuente_falsa_satisface_protocolo(self):
        with tempfile.TemporaryDirectory() as tmp:
            destino = os.path.join(tmp, "salida.mp4")
            fuente: PuertoFuenteContenido = FuenteFalsa()
            fuente.obtener("https://www.youtube.com/watch?v=abc123", destino)
            assert os.path.exists(destino)

    def test_fuente_falsa_configurada_para_fallar_lanza_error(self):
        fuente = FuenteFalsa(debe_fallar=True)
        with tempfile.TemporaryDirectory() as tmp:
            destino = os.path.join(tmp, "salida.mp4")
            with pytest.raises(ErrorObtencionContenido):
                fuente.obtener("https://www.youtube.com/watch?v=abc123", destino)
