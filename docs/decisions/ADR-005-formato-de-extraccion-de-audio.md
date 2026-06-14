# ADR-005 — Formato de extracción de audio: WAV PCM mono 16 kHz

- **Estado:** Aceptada
- **Fecha:** 2026-06-13
- **Decisores:** Fabian.
- **Fase:** Fase 3 — adaptador real de PuertoAudio.

## Contexto
El adaptador de extracción de audio (PuertoAudio) debe producir audio apto para el
motor de transcripción. Hay que fijar formato y parámetros de salida.

## Decisión
Extraer a WAV PCM mono, 16 kHz:
- 16 kHz: frecuencia estándar de los modelos de voz (Whisper opera a 16 kHz).
- Mono: un canal basta para transcripción; elimina datos redundantes.
- WAV PCM: sin pérdidas por recompresión.

## Consecuencias
### Positivas
- Archivos más livianos: ayuda al límite de tamaño por petición de la API.
- Entrada consistente para el motor, sin sorpresas de formato.
### Negativas / costos
- Re-muestrear cuesta CPU (trabajo extra de ffmpeg).
- WAV pesa más por minuto que un comprimido; mitigado por mono + 16 kHz.
## Alternativas consideradas
- Conservar el audio original sin re-muestrear: más fiel, pero archivos mayores y
  formatos heterogéneos hacia el motor. Descartada para v1.
