# ADR-006 — Troceo (chunking) de audios largos como decorador del puerto del motor

- **Estado:** Aceptada
- **Fecha:** 2026-06-13
- **Decisores:** Fabian.
- **Fase:** Fase 3/4.

## Contexto
La API de transcripción limita cada petición a ~25 min / 25 MB. RN-07 permite hasta
60 min. Además, el audio extraído es WAV PCM mono 16 kHz (ADR-005) ≈ 1.9 MB/min, por
lo que el límite que manda es el de 25 MB (~13 min), no el de 25 min. Hay que partir
los audios largos.

## Decisión
- El troceo es responsabilidad del ADAPTADOR EN LA NUBE, no del dominio.
- Se implementa como un DECORADOR (MotorConFragmentacion) que cumple el mismo Protocol
  MotorTranscripcion y envuelve a otro motor. Si la duración del audio cabe en el
  fragmento máximo, delega directamente; si no, parte el audio en ventanas de tiempo
  (PuertoAudio.recortar), transcribe cada una con el motor interno y concatena los
  textos en orden.
- Colaboradores del decorador: PuertoMetadata (duración) y PuertoAudio (recorte).
- Fragmento máximo: constante conservadora (~10 min) por debajo del límite de 25 MB
  para WAV; ajustable, a verificar en integración.

## Consecuencias
### Positivas
- Dominio y caso de uso intactos: no conocen el límite del proveedor.
- El motor local (faster-whisper, sin límite) simplemente no se envuelve.
- Reversible y aislado tras el Protocol del motor.
### Negativas / costos
- Audios largos generan varias llamadas a la API (más costo y tiempo).
- Cortes duros pueden partir una palabra en la costura (glitch menor en la
  concatenación). Aceptado para v1; mitigable luego (solapamiento / corte por silencio).

## Alternativas consideradas
- Troceo dentro de MotorOpenAI: descartada; mezcla la llamada con la lógica de troceo,
  menos testeable y no reusable.
- Troceo en el dominio (caso de uso): descartada; filtra una restricción del proveedor
  al dominio.
