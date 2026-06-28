# ADR-013 — Encuadre del frontend: monorepo y espera síncrona sin progreso ni jobs

- **Estado:** Aceptada
- **Fecha:** 2026-06-27
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — capa de presentación (Vue, ADR-003), posterior al backend de v1 completo.

## Contexto

El backend de v1 está completo y endurecido: dominio puro, capa HTTP
`POST /transcripciones` con respuesta polimórfica (ADR-009), mapeo de errores
(ADR-010), smoke e2e contra APIs vivas, hardening de path traversal (ADR-012).
Falta la única pieza pendiente de v1: el frontend Vue.

Antes de implementar se fijan dos decisiones de encuadre que condicionan todo lo
demás: dónde vive el código del frontend y cómo maneja la espera de una
transcripción que puede tardar minutos. Ambas comparten una tensión: el backend
se diseñó a conciencia como un request único, sin persistencia ni jobs
(RN-02/RN-12, ADR-008/009), y cualquier opción que lo contradiga tiene un listón
de enmienda alto.

A diferencia del backend, el frontend no se construye con TDD ni verificación de
mutación; se prioriza un flujo funcional directo. El resto de la disciplina se
mantiene (ADRs donde corresponda, CLAUDE.md vivo, código en español, flujo
dos-agentes).

## Decisión

### 1. Monorepo

El frontend vive en este mismo repositorio, como directorio `frontend/` hermano
de `src/`, no dentro de `src/` que es territorio del paquete Python. Tiene su
propio `package.json`, build y `.gitignore` para `node_modules`. `docs/`,
`specs/` y `agents/` siguen siendo transversales.

### 2. Espera síncrona bloqueante, sin canal de progreso ni jobs

El frontend dispara el `POST /transcripciones`, espera la respuesta completa y la
procesa según el contrato polimórfico: 200 = bytes para descargar; cualquier otro
status = JSON con `tipo`, `motivo`, `mensaje`. No hay progreso real: ni
SSE/streaming ni 202 + polling. El avance percibido se mitiga en el cliente:
expectativa explícita de entrada, indicador indeterminado con copy por etapas
plausibles, y timeout de cliente generoso o desactivado.

## Coherencia con decisiones previas

- **RN-02/RN-12:** respetadas al pie por ambas decisiones. Las alternativas con
  progreso real o jobs habrían exigido stashear el binario o un store de jobs,
  es decir persistencia, contra producto.
- **ADR-008/009:** la espera síncrona es la forma que ese diseño asume; el
  frontend es consumidor fiel del contrato polimórfico.
- **ADR-001:** `src/video_transcriber/` (spike congelado) y `src/transcriptorpy/`
  (activo) ya conviven bajo `src/`; `frontend/` como hermano de `src/` mantiene
  la separación limpia.

## Por qué monorepo y no repo separado

El modelo de gobernanza se apoya en una memoria única (`CLAUDE.md`), un registro
único (`docs/decisions/`) y un contrato HTTP central (ADR-009/010) que el
frontend consume. Un repo separado fragmentaría ese aparato y abriría riesgo de
divergencia contrato-consumidor sin commit atómico que los ancle. El único
beneficio del polyrepo — separar toolchains pip/npm — se logra con un
subdirectorio aislado. Se reconsideraría en v2 ante equipos separados o releases
independientes.

## Por qué espera síncrona y no progreso real ni jobs

- **SSE/streaming:** descartado. Invade el caso de uso puro y no transporta bien
  el binario final, forzando persistencia contra RN-02/12.
- **202 + polling:** descartado. Exige un store de jobs con TTL y limpieza,
  contra RN-02/12. Territorio v2.

## Consecuencias

### Positivas
- Gobernanza intacta: CLAUDE.md y docs/decisions/ siguen siendo la fuente única.
- Cero cambios de backend para soportar el frontend.
- Cambios atómicos contrato + consumidor posibles en un solo commit.

### Negativas / costos
- Conviven dos toolchains (pip/npm) en un repo; se aíslan por directorio.
- Sin progreso real, el usuario ve indicador indeterminado durante la espera.
- Timeout como limitación conocida: aceptable en local con uvicorn directo sin
  proxy; a configurar en despliegue futuro tras un reverse proxy.

## Alternativas consideradas

- **Repo separado:** descartado para v1; puerta abierta a v2.
- **SSE/streaming:** descartado.
- **202 + polling:** descartado.
