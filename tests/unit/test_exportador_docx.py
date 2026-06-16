from io import BytesIO

from docx import Document

from transcriptorpy.exportador import ExportadorDocx


def test_exportar_devuelve_docx_con_texto_exacto():
    resultado = ExportadorDocx().exportar("hola mundo")
    doc = Document(BytesIO(resultado))
    assert "\n".join(p.text for p in doc.paragraphs) == "hola mundo"
