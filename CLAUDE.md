# CLAUDE.md — Memoria persistente de TranscriptorPy

## Qué es
TranscriptorPy convierte audio o video en su texto, para LEER rápido lo que se
dijo sin ver el contenido completo. Nació de una necesidad real: transcribir una
presentación de ~25 min de un estudiante para leerla en minutos. Objetivo:
gratis, simple, sin fricción.

## Pipeline de desarrollo (obligatorio, sin saltos)
- Fase 0: idea informal — CERRADA.
- Fase 1: spec formal (actores, flujos, RN) — CERRADA (specs/spec_formal.md).
- Fase 2: Gherkin (escenarios Given/When/Then) — CERRADA (implícita en los tests).
- Fase 3: TDD (Red → Green → Refactor) — EN CURSO (muy avanzada).
- Fase 4: arquitectura emergente (surge de los tests).
- Fase 5: refactor continuo.

## Reglas que nunca se rompen
- Ninguna línea de código sin su test que falle primero.
- Ninguna regla de negocio sin su escenario Gherkin.
- Ninguna decisión de arquitectura sin su ADR.
- Ninguna ambigüedad sin resolver antes de codificar.
- El stack se decide DESPUÉS del Gherkin, nunca antes.

## Estado actual
- Fase 3 muy avanzada. Stack decidido (ADR-002/003).
- Núcleo de dominio COMPLETO y probado con dobles en memoria:
  - Validación de entrada (RN-05/06/07 + validador agregado).
  - Clasificación audio/video (es_video).
  - Caso de uso orquestador refactorizado a clase (CasoDeUsoTranscripcion) con
    cuatro puertos inyectados (motor, metadata, audio, fuente). procesar_archivo
    y procesar_url convergen en _procesar_local (RN-04: dos fuentes, un flujo).
  - Segunda fuente YouTube (RN-09): validación pura de URL (es_url_youtube) +
    PuertoFuenteContenido + adaptador real FuenteYoutubeYtdlp (yt-dlp).
  - Motivos de rechazo centralizados en Enum cerrado (MotivoRechazo, str+Enum):
    FORMATO, TAMANO, DURACION, ILEGIBLE, EXTRACCION, MOTOR, URL_INVALIDA, FUENTE,
    SIN_VOZ. El caso de uso detecta texto vacío tras strip() y devuelve
    ResultadoProcesamiento(exitoso=False, motivo=MotivoRechazo.SIN_VOZ), cubriendo RN-10.
  - Troceo de audios largos (decorador MotorConFragmentacion, ADR-006).
  - Manejo de errores RN-11: metadata ilegible, extracción fallida, motor caído.
  - Limpieza de temporales RN-12: TemporaryDirectory como context manager.
  - Exportadores de salida (RN-08): .txt nativo (ExportadorTxt), .docx con
    python-docx (ExportadorDocx), .pdf con fpdf2 + fuente DejaVu Sans Unicode
    embebida (ExportadorPdf, ADR-007). La exportación vive FUERA del caso de
    uso: CasoDeUsoTranscripcion produce texto; quien orquesta llama luego a
    seleccionar_exportador(FormatoSalida) (ADR-008).
  - Selector de exportador por formato: FormatoSalida (str+Enum cerrado con
    TXT/PDF/DOCX), Protocol Exportador y seleccionar_exportador(formato) en
    exportador.py. Test de exhaustividad garantiza que cualquier miembro nuevo
    del Enum falle en rojo si no se cablea. Función auxiliar
    metadatos_formato(FormatoSalida) → MetadatosFormato(media_type, extension)
    (NamedTuple), con su propia guardia de exhaustividad; usada por la capa HTTP.
  - Factory de composición (composicion.py): construir_caso_de_uso(config:
    ConfigTranscripcion) → CasoDeUsoTranscripcion. Ensambla MetadataFfprobe y
    AudioFfmpeg una sola vez y los pasa tanto a MotorConFragmentacion (que los
    necesita para troceo) como al caso de uso — mismas instancias. Config
    explícita (dataclass frozen, openai_api_key, ssl_cert_file: str|None=None);
    no lee entorno por dentro. Cuando ssl_cert_file no es None, construye un
    ssl.SSLContext estándar (ssl.create_default_context(cafile=ssl_cert_file))
    y lo pasa como verify a httpx.Client — habilita entornos con proxy TLS y CA
    propio (ADR-011; enmienda 2026-06-26 por deprecación de verify=<str> en httpx 0.28).
- Capa HTTP abierta con FastAPI:
  - config.py: cargar_config_desde_entorno() lee OPENAI_API_KEY y SSL_CERT_FILE
    en la frontera del sistema; lanza ErrorConfiguracion si la clave falta o
    está vacía; ssl_cert_file queda None si SSL_CERT_FILE está ausente. Respeta
    la pureza de la factory (ADR-008): la lectura del entorno ocurre aquí, fuera
    de composicion.py.
  - api.py: endpoint POST /transcripciones. Entrada multipart con archivo o URL
    de YouTube (validación de exactamente una fuente → 422 FUENTE_AUSENTE si
    ninguna o ambas). Parámetro formato con default txt; 422
    FORMATO_SALIDA_INVALIDO para valor desconocido. Respuesta polimórfica: bytes
    con Content-Type y Content-Disposition attachment (nombre fijo
    transcripcion.extensión) en éxito; JSON {tipo, motivo, mensaje} en error o
    aviso. Mapeo completo MotivoRechazo → status HTTP según ADR-010; SIN_VOZ
    devuelve 422 con tipo aviso (distinción semántica para el cliente).
    Hardening path traversal (ADR-012): el temporal del upload se nombra
    "entrada"+sufijo, donde el sufijo sale de FORMATOS_SOPORTADOS (alias público
    de formato_archivo.py); file.filename no toca la ruta. Cierre por
    construcción, no por saneo.
  - 20 tests del handler (test_api.py) ratificados por verificación de
    mutación: cada test falla por la razón correcta al remover su pieza de
    producción. Sin discrepancias. Incluye el manejador global de excepciones
    inesperadas (@app.exception_handler(Exception)) que devuelve 500 con
    {"tipo": "error", "mensaje": <cadena genérica fija>} sin filtrar internals
    (ADR-010); constante _MENSAJE_ERROR_INESPERADO como fuente única de verdad.
    Dos tests de traversal (ADR-012): contención de ruta y sufijo neutro para
    extensión no soportada; ambas ramas ratificadas por mutación.
- Cuatro adaptadores REALES verificados contra sus sistemas externos:
  - metadata → ffprobe (integración).
  - audio → ffmpeg: extraer_audio + recortar (integración).
  - motor → OpenAI gpt-4o-mini-transcribe (network; verde contra API viva).
  - fuente → yt-dlp: descarga real de YouTube verificada (network).
- Campo idioma de la transcripción: opcional — la nube no lo devuelve; un futuro
  adaptador local (faster-whisper) sí lo haría.
- Smoke test e2e CERRADO (commit d0f2133, diferido ADR-008 saldado):
  tests/integration/test_api_e2e.py ejercita construir_caso_de_uso real contra
  APIs vivas. Fixture relajar_verify_strict (function-scoped, no-autouse) en
  conftest de red limpia VERIFY_X509_STRICT sobre el SSLContext solo cuando el
  smoke la pide; producción (api.py, composicion.py) intacta.
- Tests: 101 unitarios (passed) | 9 integración (passed) | 4 de red (passed).
- Código heredado: spike funcional CONGELADO como referencia de solo lectura
  (ADR-001). No es la base de la implementación.

## Próximo paso
Frontend con Vue. El backend de v1 está completo y endurecido.

## Pendiente (en orden)
1. **Frontend con Vue.**

## Alcance
- v1: herramienta anónima de un solo uso. Entradas: archivo (audio/video) y URL
  de YouTube. Salida: texto corrido en .txt, .pdf y .docx.
- Fuera de v1 (→ v2): cuentas e historial; grabación en vivo; fuentes de URL
  distintas a YouTube; subtítulos / marcas de tiempo / hablantes.

## Decisiones (ADR)
Todas en docs/decisions/:
- ADR-001: spike existente congelado como referencia; se reconstruye test-primero;
  el stack no se hereda del spike.
- ADR-002: motor de transcripción pluggable, cloud-first (gpt-4o-mini-transcribe);
  idioma devuelto como None (la API de la nube no lo retorna; actualización 2026-06-13).
- ADR-003: stack de soporte decidido (Python, pytest, openai, ffmpeg/ffprobe).
- ADR-004: metadata (tamaño + duración) obtenida vía ffprobe subprocess + JSON.
- ADR-005: audio extraído a WAV PCM mono 16 kHz (balance calidad / tamaño para API).
- ADR-006: troceo de audios largos como decorador (MotorConFragmentacion) que
  envuelve cualquier MotorTranscripcion; dominio y caso de uso intactos.
- ADR-007: exportador PDF usa fpdf2 con fuente TrueType Unicode (DejaVu Sans)
  embebida en el paquete; pypdf solo en dev para verificar en tests.
- ADR-008: exportación FUERA del caso de uso; factory pura (composicion.py) con
  config explícita; reúso de instancias de metadata y audio; test de estructura
  valida el grafo sin I/O; humo de extremo a extremo diferido a la capa HTTP.
- ADR-009: diseño del endpoint POST /transcripciones — entrada multipart, validación
  de fuente única, parámetro formato con default txt, respuesta binaria vs JSON.
- ADR-010: mapeo de MotivoRechazo a status HTTP — FORMATO→415, TAMANO→413,
  MOTOR/FUENTE→502, resto→422; SIN_VOZ como 422 con tipo aviso.
- ADR-011: CA bundle alternativo para el cliente OpenAI — ConfigTranscripcion
  gana ssl_cert_file:str|None; cargar_config_desde_entorno lee SSL_CERT_FILE;
  composicion.py construye ssl.SSLContext estándar desde la ruta y lo pasa como
  verify a httpx.Client (enmienda 2026-06-26: migración desde verify=<str>
  deprecado en httpx 0.28). Workarounds de CA mal formado (VERIFY_X509_STRICT)
  solo en conftest de tests, nunca en producción.
- ADR-012: el nombre del temporal de upload no deriva del cliente — base fija
  "entrada" + sufijo del conjunto público FORMATOS_SOPORTADOS (alias en
  formato_archivo.py); file.filename nunca toca la ruta. Cierre por construcción.
  Enmienda (2026-06-27): el handler importa el conjunto del dominio en vez de
  duplicar la regla; una sola fuente de verdad para las extensiones soportadas.

## Agentes
- agents/analyst_agent.md — escucha y estructura; no propone tecnología.
- agents/tdd_agent.md — las tres leyes de Uncle Bob; Red-Green-Refactor.

## Estructura
```
src/transcriptorpy/
├── __init__.py
├── audio_ffmpeg.py            — adaptador real ffmpeg (PuertoAudio)
├── duracion_archivo.py        — RN-07: límite 60 min
├── formato_archivo.py         — RN-05: extensiones válidas + es_video() + FORMATOS_SOPORTADOS (alias público, consumido por api.py para ADR-012)
├── fragmentacion.py           — planificar_fragmentos() (función pura)
├── fuente_contenido.py        — PuertoFuenteContenido, FuenteFalsa, ErrorObtencionContenido
├── fuente_youtube_ytdlp.py    — adaptador real yt-dlp (FuenteYoutubeYtdlp)
├── metadata_archivo.py        — PuertoMetadata, MetadataFalsa, ErrorLecturaMetadata
├── metadata_ffprobe.py        — adaptador real ffprobe (PuertoMetadata)
├── motor_con_fragmentacion.py — decorador de troceo (ADR-006)
├── motor_openai.py            — adaptador real OpenAI (MotorTranscripcion)
├── motor_transcripcion.py     — Protocol + ResultadoTranscripcion + MotorFalso
├── assets/
│   └── DejaVuSans.ttf         — fuente Unicode embebida para ExportadorPdf
├── composicion.py             — ConfigTranscripcion + construir_caso_de_uso() (ADR-008)
├── exportador.py              — Exportador (Protocol), FormatoSalida (str+Enum),
│                                seleccionar_exportador(), ExportadorTxt/Docx/Pdf (RN-08),
│                                MetadatosFormato (NamedTuple), metadatos_formato()
├── config.py                  — cargar_config_desde_entorno() + ErrorConfiguracion
│                                (frontera: lee OPENAI_API_KEY del entorno)
├── api.py                     — FastAPI app, endpoint POST /transcripciones (ADR-009/010/012)
├── motivos.py                 — MotivoRechazo (str+Enum cerrado)
├── procesador_audio.py        — PuertoAudio, AudioFalso, ErrorProcesamientoAudio
├── procesar_transcripcion.py  — CasoDeUsoTranscripcion (clase, 4 puertos inyectados)
├── tamano_archivo.py          — RN-06: límite 1 GB
├── url_youtube.py             — es_url_youtube() (validación pura, RN-09)
└── validador_entrada.py       — validador agregado (RN-05/06/07)

specs/             — spec formal y RN
features/          — Gherkin (Fase 2, implícita en tests)
docs/decisions/    — ADR-001..ADR-010
agents/            — prompts base
tests/unit/        — 99 tests, dobles en memoria, sin I/O
tests/integration/ — 9 tests (ffmpeg/ffprobe + OpenAI + yt-dlp); marcadores integration/network
tests/fixtures/    — audio_es.wav (fixture de red)
src/video_transcriber/ — spike CONGELADO (solo lectura, ADR-001)
certs/             — CA bundle local (Avast Web Shield; no se versiona)
```

## Ritual de inicio de sesión
"Lee CLAUDE.md, agents/tdd_agent.md y specs/spec_formal.md. Confirma que
entendiste y dime en qué punto está el proyecto."
