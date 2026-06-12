# ADR-003 — Stack de soporte de v1

- **Estado:** Aceptada
- **Fecha:** 2026-06-08
- **Decisores:** Fabian.
- **Fase:** decisión de stack posterior al Gherkin (Fase 2 → Fase 3).

## Contexto
Cerrado el motor de transcripción (ADR-002), faltan las tecnologías de soporte
para implementar las RN. Se eligen DESPUÉS del Gherkin. El spike informa pero no
obliga (ADR-001).

## Decisión
- **Lenguaje:** Python.
- **Backend:** FastAPI.
- **Frontend (v1):** Vue.
- **Extracción de audio y partición en trozos** (para respetar el límite de ~25
  min por petición del motor en la nube): ffmpeg.
- **Descarga de YouTube:** yt-dlp.
- **Cliente del motor en la nube:** SDK de OpenAI (gpt-4o-mini-transcribe, ver
  ADR-002), usado SIEMPRE detrás de la abstracción del motor.
- **Exportadores:** .txt nativo; .docx con python-docx; .pdf con librería a
  confirmar al implementar (candidatas: fpdf2 o reportlab).
- **Pruebas:** behave para ejecutar los .feature en español (Fase 2) + pytest
  para tests unitarios y de integración.
- **Persistencia:** ninguna base de datos en v1; resultado efímero en memoria o
  almacenamiento temporal con TTL (RN-12).

## Alcance de esta decisión
Fija HERRAMIENTAS, no diseño. La estructura interna (capas, módulos, firmas)
emerge de los tests en Fase 3/4; este ADR no la prescribe.

## Consecuencias
- Stack alineado con la experiencia del autor (Python / FastAPI / Vue): menor
  fricción.
- Dependencias de sistema: ffmpeg y yt-dlp deben estar disponibles en el entorno
  de despliegue.
- La librería de PDF queda abierta; se decide con un test que la ejercite (puede
  ameritar una nota breve cuando se elija).
