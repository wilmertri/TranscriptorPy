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
  - Caso de uso orquestador (procesar_transcripcion): coordina metadata →
    validar → extraer audio si es video → transcribir.
  - Troceo de audios largos (decorador MotorConFragmentacion, ADR-006).
  - Manejo de errores RN-11: metadata ilegible, extracción fallida, motor caído.
  - Limpieza de temporales RN-12: TemporaryDirectory como context manager.
- Tres adaptadores REALES verificados contra sus sistemas externos:
  - metadata → ffprobe (integración; skipped sin ffprobe en PATH).
  - audio → ffmpeg: extraer_audio + recortar (integración; skipped sin ffmpeg).
  - motor → OpenAI gpt-4o-mini-transcribe (network; verde contra API viva).
- Campo idioma de la transcripción: opcional — la nube no lo devuelve; un futuro
  adaptador local (faster-whisper) sí lo haría.
- Tests: 44 unitarios (passed) | 7 integración (1 passed, 6 skipped por entorno)
  | 1 de red (passed contra API real).
- Código heredado: spike funcional CONGELADO como referencia de solo lectura
  (ADR-001). No es la base de la implementación.

## Próximo paso
Fase 3/4 — YouTube (yt-dlp, RN-09): segunda fuente de entrada, que probablemente
detone el refactor de procesar_transcripcion de función a clase/orquestador con
estado.

## Pendiente (en orden)
1. YouTube (yt-dlp, RN-09) — segunda fuente de entrada.
2. Composición/ensamblado: conectar los adaptadores reales en el caso de uso
   (AudioFfmpeg, MetadataFfprobe, MotorOpenAI con MotorConFragmentacion).
3. Exportadores de salida: .txt / .pdf / .docx (RN-08).
4. Backend HTTP con FastAPI.
5. Frontend con Vue.

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

## Agentes
- agents/analyst_agent.md — escucha y estructura; no propone tecnología.
- agents/tdd_agent.md — las tres leyes de Uncle Bob; Red-Green-Refactor.

## Estructura
```
src/transcriptorpy/
├── __init__.py
├── audio_ffmpeg.py            — adaptador real ffmpeg (PuertoAudio)
├── duracion_archivo.py        — RN-07: límite 60 min
├── formato_archivo.py         — RN-05: extensiones válidas + es_video()
├── fragmentacion.py           — planificar_fragmentos() (función pura)
├── metadata_archivo.py        — PuertoMetadata, MetadataFalsa, ErrorLecturaMetadata
├── metadata_ffprobe.py        — adaptador real ffprobe (PuertoMetadata)
├── motor_con_fragmentacion.py — decorador de troceo (ADR-006)
├── motor_openai.py            — adaptador real OpenAI (MotorTranscripcion)
├── motor_transcripcion.py     — Protocol + ResultadoTranscripcion + MotorFalso
├── procesador_audio.py        — PuertoAudio, AudioFalso, ErrorProcesamientoAudio
├── procesar_transcripcion.py  — caso de uso orquestador
├── tamano_archivo.py          — RN-06: límite 1 GB
└── validador_entrada.py       — validador agregado (RN-05/06/07)

specs/             — spec formal y RN
features/          — Gherkin (Fase 2, implícita en tests)
docs/decisions/    — ADR-001..ADR-006
agents/            — prompts base
tests/unit/        — 44 tests, dobles en memoria, sin I/O
tests/integration/ — 7 tests (ffmpeg/ffprobe + OpenAI); marcadores integration/network
tests/fixtures/    — audio_es.wav (fixture de red)
src/video_transcriber/ — spike CONGELADO (solo lectura, ADR-001)
certs/             — CA bundle local (Avast Web Shield; no se versiona)
```

## Ritual de inicio de sesión
"Lee CLAUDE.md, agents/tdd_agent.md y specs/spec_formal.md. Confirma que
entendiste y dime en qué punto está el proyecto."
