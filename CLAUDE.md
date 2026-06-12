# CLAUDE.md — Memoria persistente de TranscriptorPy

## Qué es
TranscriptorPy convierte audio o video en su texto, para LEER rápido lo que se
dijo sin ver el contenido completo. Nació de una necesidad real: transcribir una
presentación de ~25 min de un estudiante para leerla en minutos. Objetivo:
gratis, simple, sin fricción.

## Pipeline de desarrollo (obligatorio, sin saltos)
- Fase 0: idea informal — CERRADA.
- Fase 1: spec formal (actores, flujos, RN) — CERRADA (specs/spec_formal.md).
- Fase 2: Gherkin (escenarios Given/When/Then) — SIGUIENTE.
- Fase 3: TDD (Red → Green → Refactor).
- Fase 4: arquitectura emergente (surge de los tests).
- Fase 5: refactor continuo.

## Reglas que nunca se rompen
- Ninguna línea de código sin su test que falle primero.
- Ninguna regla de negocio sin su escenario Gherkin.
- Ninguna decisión de arquitectura sin su ADR.
- Ninguna ambigüedad sin resolver antes de codificar.
- El stack se decide DESPUÉS del Gherkin, nunca antes.

## Estado actual
- Fase 1 completa. Próximo paso: Fase 2 (Gherkin) a partir de RN-01..RN-12.
- Stack: SIN DECIDIR (se define tras el Gherkin).
- Código heredado: spike funcional CONGELADO como referencia de solo lectura
  (ADR-001). No es la base de la implementación.

## Alcance
- v1: herramienta anónima de un solo uso. Entradas: archivo (audio/video) y URL
  de YouTube. Salida: texto corrido en .txt, .pdf y .docx.
- Fuera de v1 (→ v2): cuentas e historial; grabación en vivo; fuentes de URL
  distintas a YouTube; subtítulos / marcas de tiempo / hablantes.

## Decisiones (ADR)
- ADR-001: el código existente se congela como spike de referencia; se
  reconstruye test-primero; el stack no se hereda del spike. (docs/decisions/)

## Agentes
- agents/analyst_agent.md — escucha y estructura; no propone tecnología.
- agents/tdd_agent.md — las tres leyes de Uncle Bob; Red-Green-Refactor.

## Estructura
- specs/ spec formal y RN | features/ Gherkin (Fase 2) | docs/decisions/ ADR
- agents/ prompts base | src/ spike congelado (solo lectura)
(schemas/, services/, models/, repositories/, routers/, tests/unit/,
tests/integration/ se crearán cuando la arquitectura emerja en Fases 3–4.)

## Ritual de inicio de sesión
"Lee CLAUDE.md, agents/tdd_agent.md y specs/spec_formal.md. Confirma que
entendiste y dime en qué punto está el proyecto."
