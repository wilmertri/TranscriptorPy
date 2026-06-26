import os

from transcriptorpy.composicion import ConfigTranscripcion


class ErrorConfiguracion(Exception):
    pass


def cargar_config_desde_entorno() -> ConfigTranscripcion:
    valor = os.environ.get("OPENAI_API_KEY")
    if valor is None or not valor.strip():
        raise ErrorConfiguracion("OPENAI_API_KEY no está definida o está vacía en el entorno")
    ssl_cert_file = os.environ.get("SSL_CERT_FILE") or None
    return ConfigTranscripcion(openai_api_key=valor, ssl_cert_file=ssl_cert_file)
