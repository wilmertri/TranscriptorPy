# ADR-007 — Librería de PDF para el exportador: fpdf2 con fuente Unicode embebida

- **Estado:** Aceptada
- **Fecha:** 2026-06-15
- **Decisores:** Fabian.
- **Fase:** Fase 3 — exportador .pdf (RN-08).

## Contexto
ADR-003 dejó la librería de PDF "por confirmar al implementar". El entregable es
texto corrido (RN-01): sin tablas, imágenes ni maquetación; solo texto → bytes PDF.
Dos consideraciones mandan:
- El idioma se detecta automáticamente (RN-03): el texto de salida puede venir en
  cualquier lengua. El exportador no puede asumir latin-1.
- v1 valora simplicidad; el exportador vive detrás de un límite reversible, así que
  la elección de librería no amarra el dominio.
Candidatas: fpdf2 y reportlab.

## Decisión
- v1 usa **fpdf2** para el exportador .pdf.
- Se embebe una fuente TrueType Unicode (**DejaVu Sans**) en el repo; el exportador
  la registra y la usa en vez de las fuentes core latin-1 de fpdf2. Así acentos,
  puntuación tipográfica y la mayoría de alfabetos (latino, cirílico, griego, etc.)
  renderizan bien, cumpliendo RN-03 de forma razonable.
- La verificación en tests reabre el PDF, extrae texto (pypdf, dependencia solo de
  test) y comprueba —con espacios normalizados— que el texto esperado está contenido.
  No se exige igualdad byte a byte: la extracción de texto de PDF no reproduce el
  original exacto.

## Consecuencias
### Positivas
- API simple y liviana, suficiente para texto corrido; Python puro.
- Cobertura amplia de idiomas por la fuente Unicode embebida (RN-03).
- Reversible: detrás del exportador, migrar a reportlab sería un cambio localizado.
### Negativas / costos
- Se añade un asset binario al repo (la TTF de DejaVu) y su carga como recurso.
- Cobertura no universal: alfabetos fuera de DejaVu —notablemente CJK— no renderizan
  en v1. Trade-off aceptado para v1 dado el caso de uso; solucionable luego sin tocar
  el dominio (otra fuente, o librería con fuentes CID).
- La aserción de tests es por contención normalizada, no igualdad exacta (límite
  inherente a la extracción de texto de PDF).

## Alternativas consideradas
- **reportlab** (descartada para v1): más potente (Platypus, fuentes CID con buen
  soporte CJK), pero más pesada y verbosa; sobredimensionada para texto corrido.
  Queda como destino de migración si v2 necesita maquetación o CJK.
- **fpdf2 solo con fuentes core (latin-1)** (descartada): rompe RN-03 — corrompe
  acentos, puntuación tipográfica y cualquier alfabeto no latino.