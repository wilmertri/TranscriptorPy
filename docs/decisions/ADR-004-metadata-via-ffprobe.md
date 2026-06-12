# ADR-004 — Lectura de metadata de archivo vía ffprobe (subproceso + JSON)

- **Estado:** Aceptada
- **Fecha:** 2026-06-08
- **Decisores:** Fabian.
- **Fase:** Fase 3 — adaptador real de PuertoMetadata.

## Contexto
El caso de uso obtiene tamaño y duración a través de PuertoMetadata (puerto ya
probado con un doble en memoria). Falta el adaptador real. Opciones:
(a) invocar ffprobe como subproceso pidiendo salida JSON;
(b) una librería de Python que envuelva la lectura de medios (ffmpeg-python,
    PyAV, pymediainfo, etc.).
ADR-003 ya declaró ffmpeg como dependencia del sistema (extracción de audio), y
ffprobe viene con ffmpeg: ya está presente, sin costo adicional.

## Decisión
- La DURACIÓN se obtiene invocando ffprobe como subproceso con salida JSON
  (p. ej. -v quiet -print_format json -show_format) y parseando el campo de
  duración.
- El TAMAÑO en bytes se obtiene del sistema de archivos (stat), no de ffprobe.
- Los fallos (binario ausente, archivo ilegible o corrupto, salida inesperada)
  se traducen a la excepción de dominio ErrorLecturaMetadata.
- El adaptador implementa el Protocol PuertoMetadata; el dominio no cambia.

## Consecuencias
### Positivas
- Cero dependencia de Python nueva: reutiliza ffmpeg/ffprobe ya requerido (ADR-003).
- Salida JSON estable y documentada; control total del mapeo de errores.
- Reversible: al vivir detrás de PuertoMetadata, migrar a una librería sería un
  cambio localizado, sin tocar el caso de uso.
### Negativas / costos
- Se maneja a mano la invocación del subproceso (código de salida, stderr,
  timeout, ruta al binario) y el parseo del JSON.
- Sus tests son de integración (tocan disco y un binario externo): más lentos y
  dependientes del entorno.

## Alternativas consideradas
- Librería envoltorio (ffmpeg-python / PyAV / pymediainfo): API más cómoda, pero
  añade dependencia y la mayoría igual requiere un binario o lib del sistema, sin
  eliminar la dependencia externa. Descartada por sumar capas sobre algo que ya
  se tiene.
- Librerías puras de Python (tinytag / mutagen): sin binario externo, pero
  cobertura limitada o poco fiable para la duración de formatos de video
  (mp4/mov). Descartada por insuficiente.
