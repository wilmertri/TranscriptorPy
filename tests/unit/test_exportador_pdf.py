import re
from io import BytesIO

import pypdf

from transcriptorpy.exportador import ExportadorPdf

TEXTO = "café añejo — Привет"


def test_exportar_devuelve_pdf_con_tokens_unicode():
    resultado = ExportadorPdf().exportar(TEXTO)

    assert resultado[:5] == b"%PDF-"
    assert len(resultado) > 0

    reader = pypdf.PdfReader(BytesIO(resultado))
    extraido = " ".join(page.extract_text() or "" for page in reader.pages)
    extraido = re.sub(r"\s+", " ", extraido).strip()

    for token in ("café", "añejo", "Привет"):
        assert token in extraido, f"Token {token!r} no encontrado en: {extraido!r}"
