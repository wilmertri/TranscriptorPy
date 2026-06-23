import pytest

from transcriptorpy.exportador import (
    ExportadorDocx,
    ExportadorPdf,
    ExportadorTxt,
    FormatoSalida,
    MetadatosFormato,
    metadatos_formato,
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


def test_todos_los_formatos_tienen_metadatos_no_vacios():
    for formato in FormatoSalida:
        meta = metadatos_formato(formato)
        assert isinstance(meta, MetadatosFormato)
        assert meta.media_type
        assert meta.extension


@pytest.mark.parametrize(
    "formato, media_type_esperado, extension_esperada",
    [
        (FormatoSalida.TXT, "text/plain", "txt"),
        (FormatoSalida.PDF, "application/pdf", "pdf"),
        (
            FormatoSalida.DOCX,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "docx",
        ),
    ],
)
def test_metadatos_formato_devuelve_media_type_y_extension_correctos(
    formato, media_type_esperado, extension_esperada
):
    meta = metadatos_formato(formato)
    assert meta.media_type == media_type_esperado
    assert meta.extension == extension_esperada
