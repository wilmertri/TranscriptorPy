from enum import Enum
from importlib.resources import files
from io import BytesIO
from typing import Protocol

from docx import Document
from fpdf import FPDF


class Exportador(Protocol):
    def exportar(self, texto: str) -> bytes: ...


class FormatoSalida(str, Enum):
    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"


class ExportadorTxt:
    def exportar(self, texto: str) -> bytes:
        return texto.encode("utf-8")


class ExportadorDocx:
    def exportar(self, texto: str) -> bytes:
        doc = Document()
        doc.add_paragraph(texto)
        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()


class ExportadorPdf:
    def exportar(self, texto: str) -> bytes:
        ttf_path = files("transcriptorpy.assets").joinpath("DejaVuSans.ttf")
        pdf = FPDF()
        pdf.add_font("DejaVu", fname=str(ttf_path))
        pdf.add_page()
        pdf.set_font("DejaVu", size=12)
        pdf.multi_cell(0, 10, texto)
        return bytes(pdf.output())


_MAPA: dict[FormatoSalida, type[Exportador]] = {
    FormatoSalida.TXT: ExportadorTxt,
    FormatoSalida.PDF: ExportadorPdf,
    FormatoSalida.DOCX: ExportadorDocx,
}


def seleccionar_exportador(formato: FormatoSalida) -> Exportador:
    return _MAPA[formato]()
