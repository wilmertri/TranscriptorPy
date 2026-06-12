# Especificación Formal — TranscriptorPy (v1)

> Fase 1 del pipeline. Documento independiente de la tecnología: describe QUÉ
> hace el sistema y bajo qué reglas, no CÓMO se implementa. El stack se decide
> después del Gherkin (ver ADR-001).

## 1. Propósito
Permitir que cualquier persona obtenga, por escrito, lo que se dice en un audio
o video, para leerlo rápido en lugar de verlo/oírlo completo. Gratis, simple y
sin registro.

## 2. Alcance
### Dentro de v1
- Transcribir desde archivo subido (audio o video).
- Transcribir desde una URL de YouTube.
- Entregar el texto como .txt, .pdf y .docx.
- Uso anónimo y de un solo uso.
### Fuera de v1 (candidatos a v2)
- Cuentas de usuario e historial de transcripciones.
- Grabación en vivo desde el navegador.
- Fuentes de URL distintas a YouTube.
- Subtítulos, marcas de tiempo o identificación de hablantes.

## 3. Actores
- **Usuario** (primario): persona anónima del público general; aporta el
  contenido, obtiene el texto y lo descarga. No se identifica ni tiene cuenta.
- **Fuente de contenido remota** (externa): servicio donde vive el video cuando
  se aporta una URL. En v1: YouTube.
- **Motor de transcripción** (externo, descrito por capacidad): convierte audio
  en texto y detecta el idioma. La tecnología concreta se decide post-Gherkin.

## 4. Flujos
### 4.1 Principal — Transcribir desde archivo
1. El Usuario llega a la app.
2. Sube un archivo de audio o video.
3. El sistema valida el archivo (formato, tamaño, duración).
4. Si es video, el sistema obtiene el audio.
5. El motor transcribe detectando el idioma automáticamente.
6. El sistema muestra el texto corrido (sin tiempos ni hablantes).
7. El Usuario elige formato (.txt, .pdf o .docx) y descarga.
8. La sesión termina; no queda nada guardado.
### 4.2 Alterno — Transcribir desde URL (YouTube)
Igual al principal, salvo el paso 2: el Usuario pega una URL de YouTube y, antes
de validar, el sistema obtiene el contenido desde la fuente remota. El resto es
idéntico.
### 4.3 Excepción
- Formato no soportado → rechazo con mensaje claro.
- Archivo demasiado grande o demasiado largo → rechazo con mensaje claro.
- URL inválida o inaccesible → error claro, no se transcribe.
- Audio sin voz reconocible → aviso explícito, sin archivo vacío.
- Fallo del motor → error claro; el Usuario puede reintentar.
- El Usuario abandona antes de descargar → la sesión expira.

## 5. Reglas de negocio
- **RN-01 — Formato del entregable:** texto corrido legible; sin marcas de
  tiempo ni identificación de hablantes.
- **RN-02 — Uso único / anonimato:** sin cuentas ni login; no se almacena nada a
  largo plazo. (Cuentas e historial: v2.)
- **RN-03 — Detección de idioma:** automática; no se le pregunta al Usuario.
- **RN-04 — Fuentes de entrada (v1):** archivo subido (audio/video) y URL de
  YouTube. Grabación en vivo: fuera de alcance.
- **RN-05 — Formatos aceptados:** audio: mp3, wav, m4a; video: mp4, mov.
  Cualquier otro se rechaza con mensaje claro.
- **RN-06 — Tamaño máximo:** 1 GB. Por encima se rechaza con mensaje claro.
- **RN-07 — Duración máxima:** 60 minutos. Por encima se rechaza con mensaje claro.
- **RN-08 — Formatos de descarga:** .txt, .pdf y .docx.
- **RN-09 — Alcance de URL:** en v1 solo URLs de YouTube. El dominio no debe
  quedar amarrado a una sola fuente: la fuente remota es extensible a futuro.
- **RN-10 — Sin voz reconocible:** si no se obtiene texto, el sistema avisa
  explícitamente y no entrega un archivo vacío.
- **RN-11 — Fallo o fuente inaccesible:** informa el error con claridad, no
  entrega transcripción a medias, y permite reintentar.
- **RN-12 — Disponibilidad del resultado:** disponible solo durante la sesión
  activa; se descarta al cerrarla o tras inactividad corta. No se almacena.

## 6. Trazabilidad
Cada RN debe tener al menos un escenario Gherkin en features/ (Fase 2) antes de
implementarse (Fase 3).
