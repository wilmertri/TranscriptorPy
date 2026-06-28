import tempfile
from pathlib import Path

from fastapi import Depends, FastAPI, Form, Request, UploadFile
from fastapi.responses import JSONResponse, Response

from transcriptorpy.composicion import construir_caso_de_uso
from transcriptorpy.config import cargar_config_desde_entorno
from transcriptorpy.exportador import FormatoSalida, metadatos_formato, seleccionar_exportador
from transcriptorpy.formato_archivo import FORMATOS_SOPORTADOS
from transcriptorpy.motivos import MotivoRechazo
from transcriptorpy.procesar_transcripcion import CasoDeUsoTranscripcion

app = FastAPI()

_MENSAJE_ERROR_INESPERADO = "Ocurrió un error inesperado."


@app.exception_handler(Exception)
async def _manejador_excepcion_inesperada(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"tipo": "error", "mensaje": _MENSAJE_ERROR_INESPERADO},
    )

_MAPA_STATUS: dict[MotivoRechazo, int] = {
    MotivoRechazo.FORMATO: 415,
    MotivoRechazo.TAMANO: 413,
    MotivoRechazo.DURACION: 422,
    MotivoRechazo.ILEGIBLE: 422,
    MotivoRechazo.EXTRACCION: 422,
    MotivoRechazo.MOTOR: 502,
    MotivoRechazo.FUENTE: 502,
    MotivoRechazo.URL_INVALIDA: 422,
    MotivoRechazo.SIN_VOZ: 422,
}

_MAPA_MENSAJES: dict[MotivoRechazo, str] = {
    MotivoRechazo.FORMATO: "El formato del archivo no está soportado.",
    MotivoRechazo.TAMANO: "El archivo supera el límite de 1 GB.",
    MotivoRechazo.DURACION: "El audio supera el límite de 60 minutos.",
    MotivoRechazo.ILEGIBLE: "No se pudo leer el archivo.",
    MotivoRechazo.EXTRACCION: "No se pudo extraer el audio del archivo.",
    MotivoRechazo.MOTOR: "El motor de transcripción no está disponible.",
    MotivoRechazo.FUENTE: "No se pudo obtener el contenido de la URL.",
    MotivoRechazo.URL_INVALIDA: "La URL no es una URL de YouTube válida.",
    MotivoRechazo.SIN_VOZ: "El audio no contiene voz reconocible.",
}


def _json_error(status: int, tipo: str, motivo: str, mensaje: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"tipo": tipo, "motivo": motivo, "mensaje": mensaje},
    )


def obtener_caso_de_uso() -> CasoDeUsoTranscripcion:
    config = cargar_config_desde_entorno()
    return construir_caso_de_uso(config)


@app.post("/transcripciones")
async def transcribir(
    file: UploadFile | None = None,
    url: str | None = Form(default=None),
    formato: str = Form(default="txt"),
    caso_de_uso: CasoDeUsoTranscripcion = Depends(obtener_caso_de_uso),
) -> Response:
    tiene_archivo = file is not None
    tiene_url = bool(url and url.strip())

    if tiene_archivo == tiene_url:
        return _json_error(
            422, "error", "FUENTE_AUSENTE",
            "Proporciona exactamente una fuente: un archivo o una URL de YouTube.",
        )

    try:
        formato_salida = FormatoSalida(formato)
    except ValueError:
        return _json_error(
            422, "error", "FORMATO_SALIDA_INVALIDO",
            f"Formato '{formato}' no soportado. Valores válidos: txt, pdf, docx.",
        )

    if tiene_archivo:
        contenido = await file.read()
        with tempfile.TemporaryDirectory() as tmp_dir:
            sufijo = Path(file.filename or "").suffix.lower()
            if sufijo not in FORMATOS_SOPORTADOS:
                sufijo = ""
            ruta = str(Path(tmp_dir) / f"entrada{sufijo}")
            Path(ruta).write_bytes(contenido)
            resultado = caso_de_uso.procesar_archivo(ruta)
    else:
        resultado = caso_de_uso.procesar_url(url)  # url no es None aquí

    if not resultado.exitoso:
        motivo = resultado.motivo
        tipo = "aviso" if motivo == MotivoRechazo.SIN_VOZ else "error"
        return _json_error(_MAPA_STATUS[motivo], tipo, motivo.value, _MAPA_MENSAJES[motivo])

    meta = metadatos_formato(formato_salida)
    cuerpo = seleccionar_exportador(formato_salida).exportar(resultado.transcripcion.texto)
    return Response(
        content=cuerpo,
        media_type=meta.media_type,
        headers={"Content-Disposition": f'attachment; filename="transcripcion.{meta.extension}"'},
    )
