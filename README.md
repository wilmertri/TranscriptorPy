# TranscriptorPy

Transcribe audio y video a **texto corrido** para leerlo rápido, sin tener que
verlo u oírlo completo. Gratis, simple y sin registro.

---

## El problema

Nació de una necesidad real: transcribir la presentación de ~25 minutos de un
video y para leerla en minutos en vez de ver completo. Las herramientas web
disponibles eran de pago, complicadas o poco útiles. TranscriptorPy es la
respuesta: subes un archivo (o pegas un enlace de YouTube), obtienes el texto y
lo descargas. Nada más.

---

## Estado del proyecto

Desarrollado con un **pipeline estricto** (ver _Metodología_). Estado actual:

| Fase | Descripción | Estado |
|------|-------------|--------|
| 0 | Idea informal | ✅ Cerrada |
| 1 | Spec formal (actores, flujos, RN-01..RN-12) | ✅ Cerrada |
| 2 | Gherkin (escenarios ejecutables) | ✅ Cerrada — trazabilidad 12/12 |
| 3 | TDD (Red → Green → Refactor) | 🔧 Muy avanzada / en curso |
| 4 | Arquitectura emergente | 🔧 Emergiendo de los tests |
| 5 | Refactor continuo | ⏳ Continuo |

**Avance de Fase 3:** núcleo de dominio **completo** y probado con dobles en
memoria — validación de entrada (RN-05/06/07), clasificación audio/video, caso
de uso orquestador (`CasoDeUsoTranscripcion`, clase con 4 puertos inyectados),
troceo de audios largos (decorador), manejo de errores (RN-11) y limpieza de
temporales (RN-12). Segunda fuente YouTube implementada (RN-09): validación pura
de URL + `PuertoFuenteContenido` + adaptador `FuenteYoutubeYtdlp` (yt-dlp).
Motivos de rechazo centralizados en `MotivoRechazo` (str+Enum cerrado, incluye `SIN_VOZ`: el caso de uso detecta texto vacío tras `strip()` y devuelve rechazo sin abrir archivo, cubriendo RN-10). Cuatro
adaptadores reales verificados contra sus sistemas: **ffprobe** (metadata),
**ffmpeg** (extracción y recorte de audio), **OpenAI gpt-4o-mini-transcribe**
(motor, verde contra API viva) y **yt-dlp** (descarga real de YouTube verificada).
Exportadores de salida implementados (RN-08): `.txt` nativo, `.docx` con
python-docx y `.pdf` con fpdf2 + fuente DejaVu Sans Unicode embebida (ADR-007).
Selector de exportador por formato (`FormatoSalida` str+Enum, `Protocol Exportador`,
`seleccionar_exportador`, `metadatos_formato`/`MetadatosFormato`). Factory de composición (`composicion.py`):
`construir_caso_de_uso(ConfigTranscripcion)` ensambla los cuatro adaptadores
reales con `MotorOpenAI` envuelto en `MotorConFragmentacion`, reusando las
mismas instancias de metadata y audio (ADR-008). **Capa HTTP en curso:**
`config.py` lee `OPENAI_API_KEY` en la frontera del sistema (`cargar_config_desde_entorno`,
`ErrorConfiguracion`); `api.py` implementa el endpoint `POST /transcripciones`
con entrada multipart (archivo o URL), validación de fuente única, formato con
default `txt`, respuesta binaria con `Content-Disposition` en éxito y JSON
`{tipo, motivo, mensaje}` en error/aviso, y mapeo completo de `MotivoRechazo`
a status HTTP (ADR-009/010). Los 18 tests del handler fueron ratificados por verificación de mutación,
incluyendo el manejador global de excepciones inesperadas (500 con esquema JSON).

Suite de pruebas: **98 unitarios** en verde · **9 de integración** (passed) · **3 de red** (passed contra APIs vivas).

---

## Alcance v1

**Dentro**
- Transcribir desde archivo subido (audio o video).
- Transcribir desde una URL de YouTube.
- Descargar el resultado en `.txt`, `.pdf` y `.docx`.
- Uso anónimo y de un solo uso.

**Fuera de v1 (candidatos a v2)**
- Cuentas de usuario e historial de transcripciones.
- Grabación en vivo desde el navegador.
- Fuentes de URL distintas a YouTube.
- Subtítulos, marcas de tiempo o identificación de hablantes.

---

## Stack

- **Lenguaje:** Python
- **Backend:** FastAPI
- **Frontend:** Vue
- **Motor de transcripción:** abstracción _pluggable_. v1 usa un adaptador en la
  nube (OpenAI `gpt-4o-mini-transcribe`); migración a local (`faster-whisper`)
  prevista sin tocar el dominio. Ver `docs/decisions/ADR-002`.
- **Extracción de audio:** ffmpeg · **Descarga de YouTube:** yt-dlp
- **Exportadores:** `.txt` nativo, `.docx` (python-docx), `.pdf` (fpdf2 + fuente Unicode embebida — ADR-007)
- **Pruebas:** pytest (unit/integration/network)
- **Persistencia:** ninguna; resultado efímero (RN-12)

El stack se decidió **después** del Gherkin, según el pipeline. Detalle en
`docs/decisions/ADR-003`.

---

## Metodología

Cada paso se construye en orden, sin saltos, y con reglas que no se rompen:

1. **Fase 0 — Idea informal:** el problema en lenguaje llano.
2. **Fase 1 — Spec formal:** actores, flujos y reglas de negocio (RN).
3. **Fase 2 — Gherkin:** cada RN expresada como escenario `Dado/Cuando/Entonces`.
4. **Fase 3 — TDD:** Red → Green → Refactor (las tres leyes de Uncle Bob).
5. **Fase 4 — Arquitectura emergente:** el diseño surge de los tests.
6. **Fase 5 — Refactor continuo:** código expresivo y limpio.

**Reglas innegociables**
- Ninguna línea de código sin su test que falle primero.
- Ninguna regla de negocio sin su escenario Gherkin.
- Ninguna decisión de arquitectura sin su ADR.
- Ninguna ambigüedad sin resolver antes de codificar.
- El stack se decide después del Gherkin, nunca antes.

---

## Estructura del repositorio

```
transcriptorpy/
├── CLAUDE.md                  # memoria persistente del proyecto
├── agents/                    # prompts base de los agentes del pipeline
│   ├── analyst_agent.md
│   └── tdd_agent.md
├── specs/
│   └── spec_formal.md         # actores, flujos y RN-01..RN-12
├── features/                  # Gherkin ejecutable (Fase 2)
│   ├── transcribir_desde_archivo.feature
│   ├── transcribir_desde_url.feature
│   ├── descargar_transcripcion.feature
│   └── sesion_anonima.feature
├── docs/decisions/            # registros de decisión de arquitectura
│   ├── ADR-001.md
│   ├── ADR-002-motor-de-transcripcion.md
│   ├── ADR-003-stack-de-soporte.md
│   ├── ADR-004-metadata-via-ffprobe.md
│   ├── ADR-005-formato-de-extraccion-de-audio.md
│   ├── ADR-006-troceo-como-decorador.md
│   ├── ADR-007-libreria-de-pdf.md
│   ├── ADR-008-composicion.md
│   ├── ADR-009-diseno-de-la-api-http.md
│   └── ADR-010-mapeo-de-errores-http.md
├── src/
│   ├── transcriptorpy/        # reconstrucción test-first (código activo)
│   │   ├── formato_archivo.py         # RN-05: extensiones válidas + es_video()
│   │   ├── tamano_archivo.py          # RN-06: límite 1 GB
│   │   ├── duracion_archivo.py        # RN-07: límite 60 min
│   │   ├── validador_entrada.py       # validador agregado (RN-05/06/07)
│   │   ├── motivos.py                 # MotivoRechazo (str+Enum cerrado)
│   │   ├── metadata_archivo.py        # PuertoMetadata + MetadataFalsa
│   │   ├── metadata_ffprobe.py        # adaptador real ffprobe
│   │   ├── procesador_audio.py        # PuertoAudio + AudioFalso
│   │   ├── audio_ffmpeg.py            # adaptador real ffmpeg (extraer + recortar)
│   │   ├── motor_transcripcion.py     # Protocol + ResultadoTranscripcion + MotorFalso
│   │   ├── motor_openai.py            # adaptador real OpenAI
│   │   ├── fragmentacion.py           # planificar_fragmentos() (función pura)
│   │   ├── motor_con_fragmentacion.py # decorador de troceo (ADR-006)
│   │   ├── fuente_contenido.py        # PuertoFuenteContenido + FuenteFalsa (RN-09)
│   │   ├── fuente_youtube_ytdlp.py    # adaptador real yt-dlp (RN-09)
│   │   ├── url_youtube.py             # es_url_youtube() — validación pura (RN-09)
│   │   ├── exportador.py              # Exportador (Protocol), FormatoSalida, seleccionar_exportador(),
│   │   │                              # ExportadorTxt, ExportadorDocx, ExportadorPdf (RN-08),
│   │   │                              # MetadatosFormato (NamedTuple), metadatos_formato()
│   │   ├── assets/
│   │   │   └── DejaVuSans.ttf         # fuente Unicode embebida para ExportadorPdf
│   │   ├── composicion.py             # ConfigTranscripcion + construir_caso_de_uso() (ADR-008)
│   │   ├── config.py                  # cargar_config_desde_entorno() + ErrorConfiguracion
│   │   ├── api.py                     # FastAPI app, POST /transcripciones (ADR-009/010)
│   │   └── procesar_transcripcion.py  # CasoDeUsoTranscripcion (clase, 4 puertos)
│   └── video_transcriber/     # spike CONGELADO — solo referencia (ADR-001)
├── tests/
│   ├── unit/                  # 94 tests — dobles en memoria, sin I/O
│   ├── integration/           # 9 tests — ffmpeg/ffprobe + OpenAI + yt-dlp
│   │   └── conftest.py        # fixtures de entorno + carga de .env
│   └── fixtures/
│       └── audio_es.wav       # audio de referencia para test de red
├── pyproject.toml
└── README.md
```

> El directorio `src/video_transcriber/` es el prototipo original, conservado
> como referencia de solo lectura. No es la base de la implementación actual.

---

## Cómo ejecutar las pruebas

```bash
# 1. Entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

# 2. Dependencias
pip install -e .[dev]

# 3a. Tests unitarios — rápidos, sin dependencias externas (98 tests)
pytest tests/unit -v

# 3b. Tests de integración — requieren ffmpeg/ffprobe en PATH; 9 tests
pytest -m integration -v

# 3c. Tests de red — llaman a APIs externas (OpenAI y YouTube vía yt-dlp); 3 tests
#     Requieren OPENAI_API_KEY definida en .env
pytest -m network -v
```

> **ffmpeg** es una dependencia del sistema, no de pip. Descárgalo desde
> [ffmpeg.org](https://ffmpeg.org/download.html) y asegúrate de que esté en el PATH.
> **yt-dlp** sí se instala vía pip (incluido en las dependencias del proyecto).

Para ejecutar únicamente los tests que no requieren recursos externos:

```bash
pytest tests/unit
```

---

## Reglas de negocio (resumen)

| RN | Descripción |
|----|-------------|
| RN-01 | Entregable en texto corrido; sin tiempos ni hablantes |
| RN-02 | Uso único / anónimo; no se almacena nada |
| RN-03 | Detección automática de idioma |
| RN-04 | Entrada: archivo (audio/video) y URL de YouTube |
| RN-05 | Formatos aceptados: mp3, wav, m4a, mp4, mov |
| RN-06 | Tamaño máximo: 1 GB |
| RN-07 | Duración máxima: 60 min |
| RN-08 | Descarga en .txt, .pdf y .docx |
| RN-09 | URL solo de YouTube en v1 (fuente extensible) |
| RN-10 | Sin voz reconocible → aviso, sin archivo vacío |
| RN-11 | Fallo o fuente inaccesible → error claro, reintentable |
| RN-12 | Resultado disponible solo durante la sesión activa |

Detalle completo en `specs/spec_formal.md`.

---

## Decisiones de arquitectura

- **ADR-001** — El código existente se congela como spike de referencia; se
  reconstruye test-first; el stack no se hereda del spike.
- **ADR-002** — Motor de transcripción _pluggable_; adaptador en la nube
  (`gpt-4o-mini-transcribe`) en v1; campo `idioma` opcional (la API cloud no lo
  devuelve; un adaptador local sí lo haría).
- **ADR-003** — Stack de soporte (FastAPI, Vue, ffmpeg, yt-dlp, pytest).
- **ADR-004** — Metadata (tamaño y duración) obtenida vía `ffprobe` subprocess
  con salida JSON; errores mapeados a `ErrorLecturaMetadata`.
- **ADR-005** — Audio extraído a WAV PCM mono 16 kHz; balance óptimo entre
  calidad y tamaño de petición a la API.
- **ADR-006** — Troceo de audios largos implementado como decorador
  (`MotorConFragmentacion`) que envuelve cualquier `MotorTranscripcion`; el
  dominio y el caso de uso no conocen el límite del proveedor.
- **ADR-007** — Exportador PDF usa `fpdf2` con fuente TrueType Unicode (DejaVu
  Sans) embebida en el paquete; cobertura latin + cirílico + griego; CJK fuera
  de v1. `pypdf` solo en dev para verificar el PDF en los tests.
- **ADR-008** — Exportación fuera del caso de uso; factory pura
  `construir_caso_de_uso(ConfigTranscripcion)` en `composicion.py`,
  independiente de FastAPI; config explícita (no lee entorno por dentro);
  `MetadataFfprobe` y `AudioFfmpeg` construidos una sola vez y compartidos entre
  `MotorConFragmentacion` y el caso de uso.
- **ADR-009** — Diseño del endpoint `POST /transcripciones`: entrada multipart,
  validación de exactamente una fuente, parámetro `formato` con default `txt`,
  respuesta binaria con `Content-Disposition` en éxito, JSON `{tipo, motivo, mensaje}`
  en error/aviso.
- **ADR-010** — Mapeo de `MotivoRechazo` a status HTTP: `FORMATO`→415,
  `TAMANO`→413, `MOTOR`/`FUENTE`→502, resto→422; `SIN_VOZ` devuelve 422 con
  `tipo: "aviso"` para distinguirlo semánticamente de un error.
- **ADR-011** — CA bundle alternativo para el cliente OpenAI: `ConfigTranscripcion`
  gana `ssl_cert_file: str | None = None`; `cargar_config_desde_entorno` lee
  `SSL_CERT_FILE` del entorno; `construir_caso_de_uso` construye
  `httpx.Client(verify=ruta)` solo cuando el campo no es `None`. Habilita
  despliegues detrás de un proxy TLS con CA propio sin alterar la pureza de la
  factory.

---

## Estado / Roadmap

### Hecho
- Núcleo de dominio completo y probado (validación, orquestación, troceo,
  manejo de errores, limpieza de temporales).
- Caso de uso refactorizado a clase (`CasoDeUsoTranscripcion`) con cuatro
  puertos inyectados; `procesar_archivo` y `procesar_url` convergen en
  `_procesar_local` (RN-04: dos fuentes, un flujo).
- Motivos de rechazo centralizados en `MotivoRechazo` (str+Enum cerrado).
- Adaptador **ffprobe** — metadata real (tamaño + duración).
- Adaptador **ffmpeg** — extracción de audio y recorte de ventanas temporales.
- Adaptador **OpenAI** — transcripción real verificada contra API viva.
- Adaptador **yt-dlp** — descarga real de audio de YouTube verificada (RN-09).
- **Exportadores** (RN-08) — `.txt` nativo, `.docx` (python-docx), `.pdf`
  (fpdf2 + DejaVu Sans Unicode embebida, ADR-007).
- **Selector de exportador** — `FormatoSalida` (str+Enum), `Protocol Exportador`,
  `seleccionar_exportador`; test de exhaustividad como guardia.
- **Composición** (ADR-008) — `construir_caso_de_uso(ConfigTranscripcion)` en
  `composicion.py`; instancias de metadata y audio compartidas; factory testeable
  sin entorno ni red.
- **Backend HTTP** — endpoint `POST /transcripciones` completo (`config.py` +
  `api.py`); manejador global de excepciones inesperadas (`@app.exception_handler
  (Exception)`) devuelve 500 con `{"tipo": "error", "mensaje": <genérico fijo>}`
  sin filtrar internals (ADR-010); 18 tests del handler ratificados por
  verificación de mutación.

### En curso
- **Smoke test e2e** (diferido de ADR-008): el test existe; pendiente ajuste del
  conftest de red para el workaround `VERIFY_X509_STRICT` del CA Avast (ADR-011).
- Hardening del nombre de archivo subido contra path traversal.

### Pendiente (en orden)
1. **Capa HTTP — completar:** humo e2e con composición real; hardening de nombre
   de archivo.
2. **Frontend** — interfaz con Vue.
