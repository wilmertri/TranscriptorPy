from transcriptorpy.exportador import ExportadorTxt


def test_exportar_devuelve_utf8_sin_modificar():
    resultado = ExportadorTxt().exportar("hola mundo")
    assert resultado.decode("utf-8") == "hola mundo"
