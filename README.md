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
| 3 | TDD (Red → Green → Refactor) | 🔧 En curso |
| 4 | Arquitectura emergente | 🔧 Emergiendo de los tests |
| 5 | Refactor continuo | ⏳ Continuo |

**Avance de Fase 3:** el bloque de **validación de entrada** está completo y
probado (formato, tamaño y duración + validador agregado con motivo de fallo).
Siguiente paso: el **puerto del motor de transcripción** y sus adaptadores.

Suite de pruebas unitarias: **15 tests en verde**.

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
- **Exportadores:** `.txt` nativo, `.docx` (python-docx), `.pdf` (por confirmar)
- **Pruebas:** pytest (unit/integration) + behave (escenarios Gherkin)
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
│   ├── ADR-001-spike-como-referencia.md
│   ├── ADR-002-motor-de-transcripcion.md
│   └── ADR-003-stack-de-soporte.md
├── src/
│   ├── transcriptorpy/        # reconstrucción test-first (código activo)
│   │   ├── formato_archivo.py
│   │   ├── tamano_archivo.py
│   │   ├── duracion_archivo.py
│   │   └── validador_entrada.py
│   └── video_transcriber/     # spike CONGELADO — solo referencia (ADR-001)
├── tests/
│   └── unit/                  # tests de la reconstrucción
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
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 2. Dependencias (según pyproject.toml)
pip install -e .[dev]            # o: pip install pytest behave

# 3. Tests unitarios (validación de entrada — 15 en verde)
pytest tests/unit -v
```

Los archivos `.feature` documentan el comportamiento esperado de cada RN. Sus
_step definitions_ se enlazan conforme avanza la Fase 3/4, a medida que el
comportamiento se implementa test-first.

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
- **ADR-002** — Motor de transcripción _pluggable_; adaptador en la nube en v1,
  migración a local prevista.
- **ADR-003** — Stack de soporte (FastAPI, Vue, ffmpeg, yt-dlp, behave/pytest).
