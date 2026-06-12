from transcriptorpy.metadata_archivo import MetadataFalsa, PuertoMetadata


def test_metadata_falsa_devuelve_tamano_y_duracion_configurados():
    puerto = MetadataFalsa(tamano_bytes=1000, duracion_segundos=42.0)
    resultado = puerto.obtener_metadata("ruta/x")
    assert resultado.tamano_bytes == 1000
    assert resultado.duracion_segundos == 42.0


def test_metadata_falsa_satisface_el_protocolo_del_puerto():
    puerto: PuertoMetadata = MetadataFalsa(tamano_bytes=500, duracion_segundos=30.0)
    resultado = puerto.obtener_metadata("audio.mp3")
    assert resultado.tamano_bytes == 500
    assert resultado.duracion_segundos == 30.0
