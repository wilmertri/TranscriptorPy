# ADR-002 — Motor de transcripción: abstracción con adaptador en la nube (cloud-first), migración a local prevista

- **Estado:** Aceptada
- **Fecha:** 2026-06-08
- **Decisores:** Fabian, con análisis comparativo de costos / precisión / hosting.
- **Fase:** decisión de stack posterior al Gherkin (Fase 2 → Fase 3).

## Contexto
El Gherkin (Fase 2) modela el motor de transcripción como una CAPACIDAD externa
(convertir audio en texto, detectar idioma), no como una tecnología. La
comparación de opciones mostró:
- Precisión: empate práctico; ambos caminos usan el mismo modelo Whisper por
  debajo (WER large-v3 ~2.5% en inglés; small ~3.4%, medium ~2.9%).
- Nube (gpt-4o-mini-transcribe ~$0.003/min): infraestructura trivial y costo
  bajo a volumen bajo, pero gasto por uso, datos a un tercero y límite de ~25
  min por petición (un archivo de 60 min se parte).
- Local (faster-whisper): gratis por uso y privado, pero hosting más pesado
  (60 min ≈ 10 min en CPU, bloquea) y necesita jobs en segundo plano.

## Decisión
1. El motor se usa SIEMPRE a través de una abstracción (un puerto del dominio);
   el código de la aplicación nunca depende de un proveedor concreto.
2. v1 se implementa con un ADAPTADOR EN LA NUBE (OpenAI gpt-4o-mini-transcribe),
   para enviar valor rápido con infraestructura mínima.
3. Un ADAPTADOR LOCAL (faster-whisper) queda previsto como migración, sin tocar
   el dominio: se cambia el adaptador, no las reglas ni los tests de negocio.
4. La FORMA concreta de la abstracción (nombres, firmas, estructura) NO se diseña
   en este ADR: emerge de los tests en Fase 3/4. Aquí se fija la decisión y su
   porqué, no el diseño.

## Consecuencias
### Positivas
- Se envía v1 sin pelear con GPU ni jobs pesados.
- Decisión reversible: migrar a local no toca el dominio ni el Gherkin.
- Costo de v1 a volumen bajo: centavos por video.
### Negativas / costos
- Gasto por minuto: escala con el uso y requiere tarjeta / gasto continuo.
- Privacidad: en v1 el audio del usuario —que puede contener voz de terceros,
  p. ej. estudiantes— se envía a un proveedor externo. Trade-off aceptado
  conscientemente para v1; la migración al adaptador local lo resuelve. No
  contradice RN-02/RN-12 (no almacenamos), pero debe ser transparente al usuario.
- Hay que partir audios de más de ~25 min para respetar el límite por petición.

## Alternativas consideradas
- Local desde v1 (descartada para v1): mejor privacidad, pero suma hosting
  pesado y jobs antes de validar el producto. Queda como destino de migración.
- Nube sin abstracción (descartada): más simple a corto plazo, pero amarra el
  proyecto a un proveedor y encarece la migración.
