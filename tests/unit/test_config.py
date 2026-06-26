import pytest

from transcriptorpy.config import ErrorConfiguracion, cargar_config_desde_entorno


def test_clave_presente_devuelve_config_con_valor_exacto(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-clave-valida")
    config = cargar_config_desde_entorno()
    assert config.openai_api_key == "sk-test-clave-valida"


def test_clave_ausente_lanza_error_configuracion(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ErrorConfiguracion):
        cargar_config_desde_entorno()


@pytest.mark.parametrize("valor", ["", "   "])
def test_clave_vacia_o_espacios_lanza_error_configuracion(monkeypatch, valor):
    monkeypatch.setenv("OPENAI_API_KEY", valor)
    with pytest.raises(ErrorConfiguracion):
        cargar_config_desde_entorno()


def test_ssl_cert_file_en_entorno_se_propaga_a_config(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("SSL_CERT_FILE", "/ruta/bundle.pem")
    config = cargar_config_desde_entorno()
    assert config.ssl_cert_file == "/ruta/bundle.pem"


def test_ssl_cert_file_ausente_deja_campo_none(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("SSL_CERT_FILE", raising=False)
    config = cargar_config_desde_entorno()
    assert config.ssl_cert_file is None
