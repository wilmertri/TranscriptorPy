# Verificación por mutación — `test_api.py`

## Mecanismo de respaldo

`api.py` no está trackeado en git (archivo nuevo sin commitear). Se usó una copia literal al directorio scratchpad de sesión con verificación de hash SHA-256 (`B123C722D2817F39314885BA5B010B2DC8186B693D9941545B65C027960397FD`). Cada restauración fue verificada antes de continuar con la siguiente mutación.

Línea base confirmada antes de empezar: **94 passed**.

---

## Resultados por mutación

### Mutación 1 — Binario exitoso roto

Reemplazada la rama de respuesta exitosa por `Response(content=b"", media_type="application/octet-stream")`.

**Tests fallidos (5):**
- `test_post_transcripciones_archivo_txt_happy_path` — `content-type` recibido: `application/octet-stream`, esperado: `text/plain`
- `test_post_transcripciones_respuesta_exitosa_incluye_content_disposition` — `KeyError: 'content-disposition'` (header ausente)
- `test_post_transcripciones_formato_ausente_usa_txt_por_defecto` — `content-type` recibido: `application/octet-stream`
- `test_post_transcripciones_url_happy_path` — `content-type` recibido: `application/octet-stream`
- `test_post_transcripciones_url_content_disposition_usa_extension_correcta` — `KeyError: 'content-disposition'`

**Tests de error (12):** todos pasaron.

---

### Mutación 2 — Content-Disposition eliminado

Quitado el `headers={"Content-Disposition": ...}` del `Response` exitoso, dejando `content` y `media_type` intactos.

**Tests fallidos (2):**
- `test_post_transcripciones_respuesta_exitosa_incluye_content_disposition`
- `test_post_transcripciones_url_content_disposition_usa_extension_correcta`

Los demás happy-path (status, body, content-type) siguieron pasando.

---

### Mutación 3 — Default de formato eliminado

Cambiado `formato: str = Form(default="txt")` a `formato: str = Form()` (campo requerido).

**Tests fallidos (1):**
- `test_post_transcripciones_formato_ausente_usa_txt_por_defecto` — FastAPI devolvió 422 Unprocessable Entity por campo requerido faltante; el test esperaba 200.

Sin efectos colaterales: todos los demás tests envían `formato` explícito.

---

### Mutación 4 — Validación de fuente única eliminada

Eliminado el bloque `if tiene_archivo == tiene_url: return _json_error(...)`.

**Tests fallidos (2):**
- `test_post_transcripciones_sin_fuente_devuelve_422_fuente_ausente` — recibió 200 OK (el `CasoDeUsoFalso` absorbió la llamada con `url=None` devolviendo el resultado exitoso cableado)
- `test_post_transcripciones_ambas_fuentes_devuelve_422_fuente_ausente` — recibió 200 OK (la rama de archivo se ejecutó y el doble devolvió éxito)

Sin efectos colaterales sobre otros tests.

---

### Mutación 5 — Formato inválido sin captura

Eliminado el `try/except ValueError` alrededor de `FormatoSalida(formato)`.

**Tests fallidos (1):**
- `test_post_transcripciones_formato_invalido_devuelve_422_formato_salida_invalido`

Nota: el fallo no fue un HTTP 500 sino una excepción de Python propagada hasta el `TestClient` de Starlette (`ValueError: 'xml' is not a valid FormatoSalida`), que la relanzó hacia el test.

---

### Mutación 6 — Mapeo de status siempre 400

Reemplazado `_MAPA_STATUS[motivo]` por el literal `400`.

**Tests fallidos (9):**
- `[FORMATO-415]` — recibió 400, esperaba 415
- `[TAMANO-413]` — recibió 400, esperaba 413
- `[DURACION-422]` — recibió 400, esperaba 422
- `[ILEGIBLE-422]` — recibió 400, esperaba 422
- `[EXTRACCION-422]` — recibió 400, esperaba 422
- `[MOTOR-502]` — recibió 400, esperaba 502
- `[FUENTE-502]` — recibió 400, esperaba 502
- `[URL_INVALIDA-422]` — recibió 400, esperaba 422
- `test_post_transcripciones_sin_voz_devuelve_422_con_tipo_aviso` — recibió 400, esperaba 422

Los 8 tests de camino feliz y validación de transporte pasaron.

Nota: los casos que esperaban 422 (DURACION, ILEGIBLE, EXTRACCION, URL_INVALIDA, SIN_VOZ) también fallaron porque 400 ≠ 422. El enunciado indicaba que «podrían no fallar por status» — en la práctica sí fallaron, lo que confirma cobertura completa.

---

### Mutación 7 — tipo siempre "error"

Reemplazado `tipo = "aviso" if motivo == MotivoRechazo.SIN_VOZ else "error"` por `tipo = "error"`.

**Tests fallidos (1):**
- `test_post_transcripciones_sin_voz_devuelve_422_con_tipo_aviso` — `body["tipo"]` recibido: `"error"`, esperado: `"aviso"`

Los 8 casos del parametrizado (que afirman `tipo == "error"`) pasaron sin perturbación.

---

## Verde final

Tras restaurar `api.py` por séptima vez: **94 passed, 0 failed**.
Hash de `api.py` verificado idéntico al original.

---

## Tabla resumen

| # | Mutación | Tests que esperábamos que fallaran | Tests que realmente fallaron | Veredicto |
|---|---|---|---|---|
| 1 | Binario exitoso roto | Happy-path de archivo, default-formato y URL (los que afirman status/body/Content-Type) | `archivo_txt_happy_path`, `respuesta_exitosa_incluye_content_disposition`, `formato_ausente_usa_txt_por_defecto`, `url_happy_path`, `url_content_disposition_usa_extension_correcta` (5) | ✅ Coincide — los 3 del enunciado fallaron; los 2 de Content-Disposition también, lógicamente, al borrar la rama entera |
| 2 | Content-Disposition eliminado | Los 2 tests que afirman el header Content-Disposition | `respuesta_exitosa_incluye_content_disposition`, `url_content_disposition_usa_extension_correcta` (2) | ✅ Coincide exacto |
| 3 | Default de formato eliminado | El test que omite el campo formato | `formato_ausente_usa_txt_por_defecto` (1) | ✅ Coincide exacto — sin efectos colaterales |
| 4 | Validación de fuente única eliminada | Los 2 tests de FUENTE_AUSENTE | `sin_fuente_devuelve_422_fuente_ausente`, `ambas_fuentes_devuelve_422_fuente_ausente` (2) | ✅ Coincide exacto — sin efectos colaterales |
| 5 | Formato inválido sin captura | El test del formato xml | `formato_invalido_devuelve_422_formato_salida_invalido` (1) | ✅ Coincide exacto — fallo como excepción Python, no HTTP 500 |
| 6 | Mapeo de status siempre 400 | FORMATO-415, TAMANO-413, MOTOR-502, FUENTE-502 (los ≠ 400) | Los 8 del parametrizado + `sin_voz_devuelve_422_con_tipo_aviso` (9) | ✅ Coincide — los 422 también fallaron (400 ≠ 422); confirma cobertura completa del mapa |
| 7 | tipo siempre "error" | Solo el test de SIN_VOZ que afirma `tipo == "aviso"` | `sin_voz_devuelve_422_con_tipo_aviso` (1) | ✅ Coincide exacto |

**No hay discrepancias.** Ningún test falló de menos (cobertura hueca) ni hubo acoplamientos inesperados que generaran falsos positivos. La suite de `test_api.py` es genuina.
