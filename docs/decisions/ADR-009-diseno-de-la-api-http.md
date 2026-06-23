# ADR-009 — Diseño de la API HTTP: endpoint único, respuesta polimórfica, config en la frontera

- **Estado:** Aceptada
- **Fecha:** 2026-06-15
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — capa HTTP (FastAPI, ADR-003).

## Contexto
El dominio está completo y verde: `CasoDeUsoTranscripcion` (clase con cuatro
puertos) no lanza excepciones hacia afuera, sino que devuelve siempre un
`ResultadoProcesamiento(exitoso, transcripcion, motivo)`; los rechazos viajan
como `MotivoRechazo` (Enum cerrado: FORMATO, TAMANO, DURACION, ILEGIBLE,
EXTRACCION, MOTOR, URL_INVALIDA, FUENTE, SIN_VOZ). La exportación vive FUERA del
caso de uso (ADR-008): quien orquesta produce texto y luego llama a
`seleccionar_exportador(FormatoSalida)`. La factory `construir_caso_de_uso(
ConfigTranscripcion)` es pura: recibe config explícita, no lee entorno.

Falta exponer esto por HTTP. Hay que fijar la FORMA de la API (entrada, salida,
frontera de config, testabilidad), no los códigos de estado concretos por
motivo: eso es ADR-010. Este ADR fija la forma; ADR-010 fija los números.

## Decisión

### 1. Endpoint único: `POST /transcripciones`
Un solo endpoint, recurso en plural. El verbo HTTP `POST` carga el "crear"; la
ruta nombra el recurso, no la acción. No se persiste nada (RN-02/RN-12): no hay
recurso que perdure ni URL que devolver, pero la semántica de creación se
mantiene.

### 2. Entrada: `multipart/form-data`
Como subir archivo obliga a multipart, la URL entra también como campo de
formulario (no JSON: no se mezclan body JSON y multipart cómodamente). Campos:
- `file: UploadFile | None`
- `url: str | None`
- `formato: str | None`

**Regla "exactamente una fuente".** Cuatro combinaciones de (file, url); solo
"solo archivo" y "solo URL" proceden. "Ninguna" y "ambas" son request mal
formado. Esta validación NO es un `MotivoRechazo`: el dominio asume que ya tiene
una fuente; "no diste exactamente una fuente" es un problema de transporte. Vive
en el handler, mapea a 4xx (ADR-010), no toca el Enum.

**`formato` ausente vs inválido** (distinción deliberada, no colapsar):
- **Ausente** → default `.txt`. `.txt` es el formato más simple y sin pérdida
  (texto corrido es lo que promete RN-01); la ausencia es inequívoca. Default
  benigno.
- **Presente pero desconocido** (p. ej. `xml`) → 422. Mandaste algo y era
  inválido; tragárselo y devolver `.txt` ocultaría el error del cliente. Es un
  rechazo de transporte (como "ninguna/ambas fuentes"), NO un `MotivoRechazo`.

### 3. Salida: polimórfica, dos sobres
La respuesta no es siempre lo mismo. El handler bifurca según el
`ResultadoProcesamiento`:

- **Éxito con texto** (`exitoso=True`, texto no vacío) → **sobre binario**: los
  bytes del archivo exportado, con `Content-Type` del formato y
  `Content-Disposition` con nombre de archivo.
- **Todo lo demás** (aviso SIN_VOZ y cualquier rechazo o error de transporte) →
  **sobre JSON**, con un ESQUEMA COMÚN.

**Esquema JSON común** para aviso y error:
```
{ "tipo": "aviso" | "error", "motivo": "<clave de máquina>", "mensaje": "<texto legible>" }
```
- `tipo` discrimina aviso (SIN_VOZ) de error (rechazos y transporte).
- `motivo` es la clave de máquina: el valor del `MotivoRechazo`, o un motivo de
  transporte (`FUENTE_AUSENTE`, `FORMATO_SALIDA_INVALIDO`).
- `mensaje` es texto legible para mostrar al usuario.

Un solo contrato JSON para el frontend: parsea una forma, ramifica por `tipo` y,
si necesita lógica fina, por `motivo`.

**El `motivo` de máquina NO es el status HTTP.** Un mismo 422 puede llevar
`motivo` DURACION, URL_INVALIDA o FUENTE_AUSENTE: el status agrupa, el `motivo`
precisa. El frontend que quiera decir "el video es muy largo" lee `motivo`, no
el número. Por eso el esquema común no pierde información frente a dos esquemas.

**El cliente discrimina por `Content-Type`, no por status.** SIN_VOZ viaja como
JSON con status 200 (lean de ADR-010): un 200 puede ser bytes (éxito) o JSON
(aviso). El cliente lee primero el `Content-Type` de la respuesta, después el
cuerpo. Es RESTful y correcto, pero condiciona al cliente: Content-Type primero.

### 4. Nombre del archivo de descarga: base fija anónima
`Content-Disposition` con `transcripcion.{ext}`. Base FIJA, no derivada del
nombre del archivo subido ni del título del video de YouTube. RN-02 (anonimato):
el archivo de origen puede llevar el nombre de un tercero —p. ej. un
estudiante— que no tiene por qué viajar de vuelta. La extensión sale del mapa de
dominio (ver Dependencias).

### 5. Config en la frontera, factory pura intacta
Una función `cargar_config_desde_entorno() -> ConfigTranscripcion` lee
`OPENAI_API_KEY` del entorno y falla con error claro si falta. Se llama una sola
vez al arrancar la app (la key no cambia entre peticiones). El caso de uso se
expone como dependencia inyectable (`Depends`). La factory pura del ADR-008
queda intacta: la lectura de entorno vive en este único punto de la frontera
HTTP, no dentro de la factory.

### 6. Testabilidad de la capa
- Tests rápidos del handler: caso de uso expuesto vía `Depends`, sustituido en
  test con `app.dependency_overrides` + un caso de uso falso, con `TestClient`.
  Cubren ruteo, parseo multipart, validación de fuente única, default/inválido
  de formato, mapeo de errores, streaming de bytes y headers — sin tocar OpenAI
  ni ffmpeg. Tier rápido.
- Humo end-to-end con la composición REAL (`construir_caso_de_uso`): el que
  ADR-008 dejó explícitamente diferido "a la capa HTTP". Se cierra aquí como
  test marcado aparte (integration/network), no en el tier rápido.

## Dependencias que este ADR consume pero no posee
- **Mapa `formato → (media-type, extensión)`**: vive en el dominio, junto a
  `FormatoSalida`, como función paralela a `seleccionar_exportador` (misma casa,
  misma guardia de exhaustividad). NO existe todavía: es prerrequisito del
  handler (sin él no se arma el sobre binario). Se construye test-first en su
  propio micro-ciclo antes del primer rojo de FastAPI. Es código de dominio, no
  de transporte.
- **Mapeo `MotivoRechazo → status HTTP`** y los códigos concretos: ADR-010.

## Lo que este ADR explícitamente NO decide
Los códigos de estado concretos por motivo (incluido qué status lleva SIN_VOZ y
si ILEGIBLE/EXTRACCION son 4xx o 5xx). Eso es ADR-010. Este ADR fija la FORMA;
ADR-010 fija los NÚMEROS.

## Consecuencias
### Positivas
- Un solo endpoint y un solo contrato JSON: superficie mínima para el frontend.
- La factory pura del ADR-008 no se toca; la config queda en un único punto.
- El handler es delgado: bifurca sobre `ResultadoProcesamiento`, sin `try/except`
  de errores de dominio (el caso de uso ya los tradujo). El `try/except` queda
  solo para lo inesperado (bug) → 500.
- Toda la capa es testeable en el tier rápido con dobles; el e2e real cierra el
  diferido del ADR-008.
### Negativas / costos
- Respuesta polimórfica: el cliente debe mirar `Content-Type` antes del cuerpo,
  no puede ramificar solo por status. Complejidad real, asumida a cambio de ser
  RESTful (SIN_VOZ como 200).
- `multipart` para todo (incluida la URL) es menos elegante que un JSON, pero lo
  impone el archivo.

## Alternativas consideradas
- **Dos endpoints (uno por fuente)**: descartada. El dominio ya unificó archivo y
  URL en `_procesar_local` (RN-04: dos fuentes, un flujo); un endpoint con
  "exactamente una fuente" espeja esa convergencia.
- **URL por JSON, archivo por multipart (dos content-types)**: descartada.
  Complica el cliente y el handler sin ganancia; multipart admite ambos.
- **Dos esquemas JSON (aviso vs error)**: descartada. Un esquema común con campo
  `tipo` da al frontend un solo parser sin perder precisión (la da `motivo`).
- **`formato` obligatorio sin default**: descartada a favor de default `.txt`
  por robustez de la API fuera del frontend; el caso "inválido" sigue siendo 422,
  así que no se pierde señal de error.
- **Nombre de descarga derivado del origen**: descartada por RN-02 (filtraría el
  nombre de archivo/título de un tercero).
- **Leer `OPENAI_API_KEY` dentro de la factory**: descartada; rompería la pureza
  del ADR-008. La config se lee en la frontera y se inyecta.
