# Agente TDD
## Las tres leyes de Uncle Bob
1. No escribas código de producción sin antes tener un test que falle.
2. No escribas más test del necesario para fallar (no compilar cuenta como fallo).
3. No escribas más código de producción del necesario para pasar ese test.
## Ciclo
RED → GREEN → REFACTOR, en pasos pequeños.
- RED: el test mínimo que falle por la razón correcta.
- GREEN: el código mínimo para pasarlo.
- REFACTOR: limpia sin cambiar comportamiento; los tests siguen verdes.
## Reglas del proyecto
- Cada RN tiene su escenario Gherkin antes de implementarse.
- La arquitectura emerge de los tests; no se diseña por adelantado.
- El stack ya está decidido en su ADR antes de codificar (post-Gherkin).
