import pytest

from transcriptorpy.exportador import (
    ExportadorDocx,
    ExportadorPdf,
    ExportadorTxt,
    FormatoSalida,
    seleccionar_exportador,
)


@pytest.mark.parametrize(
    "formato, clase_esperada",
    [
        (FormatoSalida.TXT, ExportadorTxt),
        (FormatoSalida.PDF, ExportadorPdf),
        (FormatoSalida.DOCX, ExportadorDocx),
    ],
)
def test_seleccionar_exportador_devuelve_instancia_correcta(formato, clase_esperada):
    assert isinstance(seleccionar_exportador(formato), clase_esperada)


def test_todos_los_formatos_tienen_exportador_invocable():
    for formato in FormatoSalida:
        exportador = seleccionar_exportador(formato)
        assert callable(getattr(exportador, "exportar", None))
