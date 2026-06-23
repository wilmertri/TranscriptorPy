import pytest
from fastapi.testclient import TestClient

from transcriptorpy.api import app, obtener_caso_de_uso
from transcriptorpy.exportador import FormatoSalida, seleccionar_exportador
from transcriptorpy.motivos import MotivoRechazo
from transcriptorpy.motor_transcripcion import ResultadoTranscripcion
from transcriptorpy.procesar_transcripcion import ResultadoProcesamiento


class CasoDeUsoFalso:
    def __init__(self, resultado: ResultadoProcesamiento) -> None:
        self._resultado = resultado

    def procesar_archivo(self, nombre: str) -> ResultadoProcesamiento:
        return self._resultado

    def procesar_url(self, url: str) -> ResultadoProcesamiento:
        return self._resultado


_TEXTO = "hola mundo"
_RESULTADO_EXITOSO = ResultadoProcesamiento(
    exitoso=True,
    transcripcion=ResultadoTranscripcion(texto=_TEXTO, idioma=None),
)


@pytest.fixture
def cliente_exitoso():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Happy path — archivo
# ---------------------------------------------------------------------------


def test_post_transcripciones_archivo_txt_happy_path(cliente_exitoso):
    respuesta = cliente_exitoso.post(
        "/transcripciones",
        files={"file": ("audio.mp3", b"bytes-de-prueba", "audio/mpeg")},
        data={"formato": "txt"},
    )
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")
    esperado = seleccionar_exportador(FormatoSalida.TXT).exportar(_TEXTO)
    assert respuesta.content == esperado


def test_post_transcripciones_respuesta_exitosa_incluye_content_disposition(cliente_exitoso):
    respuesta = cliente_exitoso.post(
        "/transcripciones",
        files={"file": ("audio.mp3", b"bytes-de-prueba", "audio/mpeg")},
        data={"formato": "txt"},
    )
    assert respuesta.status_code == 200
    assert 'filename="transcripcion.txt"' in respuesta.headers["content-disposition"]


def test_post_transcripciones_formato_ausente_usa_txt_por_defecto(cliente_exitoso):
    respuesta = cliente_exitoso.post(
        "/transcripciones",
        files={"file": ("audio.mp3", b"bytes-de-prueba", "audio/mpeg")},
    )
    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")


# ---------------------------------------------------------------------------
# Happy path — URL
# ---------------------------------------------------------------------------


def test_post_transcripciones_url_happy_path():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    try:
        cliente = TestClient(app)
        respuesta = cliente.post(
            "/transcripciones",
            data={"url": "https://www.youtube.com/watch?v=test", "formato": "txt"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")
    esperado = seleccionar_exportador(FormatoSalida.TXT).exportar(_TEXTO)
    assert respuesta.content == esperado


def test_post_transcripciones_url_content_disposition_usa_extension_correcta():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    try:
        cliente = TestClient(app)
        respuesta = cliente.post(
            "/transcripciones",
            data={"url": "https://www.youtube.com/watch?v=test", "formato": "pdf"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 200
    assert 'filename="transcripcion.pdf"' in respuesta.headers["content-disposition"]


# ---------------------------------------------------------------------------
# Validación de transporte — FUENTE_AUSENTE y FORMATO_SALIDA_INVALIDO
# ---------------------------------------------------------------------------


def test_post_transcripciones_sin_fuente_devuelve_422_fuente_ausente():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    try:
        respuesta = TestClient(app).post("/transcripciones", data={"formato": "txt"})
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 422
    body = respuesta.json()
    assert body["tipo"] == "error"
    assert body["motivo"] == "FUENTE_AUSENTE"


def test_post_transcripciones_ambas_fuentes_devuelve_422_fuente_ausente():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    try:
        respuesta = TestClient(app).post(
            "/transcripciones",
            files={"file": ("audio.mp3", b"bytes", "audio/mpeg")},
            data={"url": "https://www.youtube.com/watch?v=test", "formato": "txt"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 422
    assert respuesta.json()["motivo"] == "FUENTE_AUSENTE"


def test_post_transcripciones_formato_invalido_devuelve_422_formato_salida_invalido():
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(_RESULTADO_EXITOSO)
    try:
        respuesta = TestClient(app).post(
            "/transcripciones",
            files={"file": ("audio.mp3", b"bytes", "audio/mpeg")},
            data={"formato": "xml"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 422
    body = respuesta.json()
    assert body["tipo"] == "error"
    assert body["motivo"] == "FORMATO_SALIDA_INVALIDO"


# ---------------------------------------------------------------------------
# Motivos de dominio → status HTTP (ADR-010)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "motivo,status_esperado",
    [
        (MotivoRechazo.FORMATO, 415),
        (MotivoRechazo.TAMANO, 413),
        (MotivoRechazo.DURACION, 422),
        (MotivoRechazo.ILEGIBLE, 422),
        (MotivoRechazo.EXTRACCION, 422),
        (MotivoRechazo.MOTOR, 502),
        (MotivoRechazo.FUENTE, 502),
        (MotivoRechazo.URL_INVALIDA, 422),
    ],
)
def test_post_transcripciones_motivo_dominio_devuelve_status_y_tipo_error(
    motivo, status_esperado
):
    resultado = ResultadoProcesamiento(exitoso=False, motivo=motivo)
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(resultado)
    try:
        respuesta = TestClient(app).post(
            "/transcripciones",
            files={"file": ("audio.mp3", b"bytes", "audio/mpeg")},
            data={"formato": "txt"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == status_esperado
    body = respuesta.json()
    assert body["tipo"] == "error"
    assert body["motivo"] == motivo.value


def test_post_transcripciones_sin_voz_devuelve_422_con_tipo_aviso():
    resultado = ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.SIN_VOZ)
    app.dependency_overrides[obtener_caso_de_uso] = lambda: CasoDeUsoFalso(resultado)
    try:
        respuesta = TestClient(app).post(
            "/transcripciones",
            files={"file": ("audio.mp3", b"bytes", "audio/mpeg")},
            data={"formato": "txt"},
        )
    finally:
        app.dependency_overrides.clear()

    assert respuesta.status_code == 422
    body = respuesta.json()
    assert body["tipo"] == "aviso"
    assert body["motivo"] == "SIN_VOZ"
