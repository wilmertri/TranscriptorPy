# ADR-010 — Mapeo de motivos de rechazo y errores a códigos de estado HTTP

- **Estado:** Aceptada
- **Fecha:** 2026-06-15
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — capa HTTP (FastAPI, ADR-003).

## Contexto
ADR-009 fijó la FORMA de la API: endpoint único `POST /transcripciones`,
respuesta polimórfica (sobre binario en éxito, sobre JSON común
`{tipo, motivo, mensaje}` en todo lo demás). Quedó pendiente, por decisión
explícita de ADR-009, fijar los NÚMEROS: qué código de estado HTTP lleva cada
motivo.

El dominio devuelve `ResultadoProcesamiento` con un `MotivoRechazo` (Enum
cerrado, nueve miembros). La capa HTTP añade motivos de TRANSPORTE que no son del
dominio (validaciones del request previas a invocar el caso de uso). Y queda el
catch-all de lo inesperado (bug). Este ADR mapea los tres conjuntos a status,
sin huecos, para que el conjunto de claves `motivo` que el frontend puede recibir
quede completo y cerrado.

## Decisión

### Tabla de mapeo
| `motivo` | `tipo` | status | razonamiento |
|---|---|---|---|
| FUENTE_AUSENTE | error | 422 | transporte: ninguna o ambas fuentes (request mal formado) |
| FORMATO_SALIDA_INVALIDO | error | 422 | transporte: `formato` presente pero desconocido |
| FORMATO | error | 415 | Unsupported Media Type: entrada no soportada (RN-05) |
| TAMANO | error | 413 | Payload Too Large: supera 1 GB (RN-06) |
| DURACION | error | 422 | restricción semántica, no de bytes: supera 60 min (RN-07) |
| URL_INVALIDA | error | 422 | input inválido: la URL no es de YouTube (RN-09) |
| ILEGIBLE | error | 422 | ver "Limitación conocida" |
| EXTRACCION | error | 422 | ver "Limitación conocida" |
| MOTOR | error | 502 | upstream OpenAI falla (RN-11, reintentable) |
| FUENTE | error | 502 | upstream YouTube inaccesible (RN-11, reintentable) |
| SIN_VOZ | **aviso** | 422 | ver "SIN_VOZ" abajo |
| (inesperado) | error | 500 | bug no previsto: el único 5xx por culpa nuestra real |

### SIN_VOZ — 422 con `tipo: "aviso"` (híbrido deliberado)
El request fue válido, el procesamiento corrió completo, el motor hizo su
trabajo: simplemente no había voz que transcribir (RN-10). No hay entregable, y
el Gherkin exige avisar sin entregar un archivo vacío.

- **status 422**: la operación no produjo un entregable. El status se lee como
  "no hay archivo para vos", agrupando SIN_VOZ con los demás casos sin
  entregable; NO se lee como "vos hiciste algo mal".
- **`tipo: "aviso"`**: la naturaleza NO es de error. El sistema funcionó, no hubo
  culpa del cliente. El frontend muestra el mensaje en tono informativo (no rojo
  de error) leyendo `tipo`, aunque el status sea 4xx.

Es un híbrido consciente: el status agrupa a nivel transporte ("sin entregable"),
el `tipo` matiza la naturaleza ("aviso, no error"). Preserva la razón por la que
el esquema común tiene el campo `tipo` (SIN_VOZ ES distinto de un rechazo de
formato); colapsarlo a `tipo: "error"` vaciaría el campo de sentido (quedaría con
un solo valor posible en todos los casos).

### Coherencia con ADR-009
Con SIN_VOZ en 422 (no 200), el contrato de salida se simplifica: **status 200 es
siempre el sobre binario; cualquier otro código es JSON.** El cliente ramifica
por status (200 vs no-200) y, dentro del JSON, por `tipo` (aviso vs error) y por
`motivo` (clave fina). El `motivo` NO es el status: un mismo 422 puede llevar
DURACION, URL_INVALIDA, FUENTE_AUSENTE, FORMATO_SALIDA_INVALIDO, ILEGIBLE,
EXTRACCION o SIN_VOZ — el status agrupa, el `motivo` precisa.

### Familias de status usadas
- **413 / 415**: códigos precisos para TAMANO y FORMATO; semánticamente exactos,
  preferidos sobre un 422 genérico cuando el código específico existe.
- **422**: cajón de "request procesable en forma pero rechazado por regla"
  (DURACION, URL_INVALIDA, los de transporte, ILEGIBLE/EXTRACCION, SIN_VOZ).
- **502**: dependencia upstream falla (MOTOR, FUENTE). Reintentable (RN-11).
- **500**: SOLO para lo inesperado (bug). El caso de uso no lanza excepciones de
  dominio hacia afuera (devuelve `ResultadoProcesamiento`), así que el `try/except`
  del handler queda reservado a lo genuinamente imprevisto.

## Limitación conocida — ILEGIBLE y EXTRACCION como 422
El dominio colapsa en un solo motivo dos causas de naturaleza distinta:
- **ILEGIBLE**: el archivo del usuario está corrupto (culpa del cliente → 4xx)
  O ffprobe está ausente/roto en el servidor (culpa nuestra → 5xx).
- **EXTRACCION**: el audio no se pudo extraer del archivo (culpa del cliente)
  O ffmpeg está ausente/roto (culpa nuestra).

HTTP no puede distinguir porque el motivo no distingue. Se elige **422 para
ambas** por dos razones: en producción, con los binarios instalados y verificados
(hay tests de integración verdes contra ffmpeg/ffprobe reales), la causa
abrumadoramente probable es el archivo del usuario; y un 5xx dispararía alertas
de "servidor caído" cuando el servidor está sano y el problema es un archivo
corrupto.

**Costo asumido:** si algún día ffmpeg/ffprobe desaparece del PATH en despliegue,
el cliente verá 422 ("tu archivo no se pudo leer") cuando la causa real es una
mala configuración del servidor — diagnóstico engañoso. Se acepta para v1. La
solución más pura (que el dominio DISTINGA las dos causas: dos motivos, o un
motivo con detalle de culpa) es cirugía en el dominio que no se hace ahora por un
caso de borde operativo; queda como mejora futura si el problema se materializa.

## Conjunto cerrado de claves `motivo`
El frontend puede recibir exactamente estas claves y ninguna otra:
- De dominio (`MotivoRechazo`): FORMATO, TAMANO, DURACION, ILEGIBLE, EXTRACCION,
  MOTOR, URL_INVALIDA, FUENTE, SIN_VOZ.
- De transporte (solo HTTP, no en el Enum del dominio): FUENTE_AUSENTE,
  FORMATO_SALIDA_INVALIDO.
- El 500 inesperado no necesariamente lleva `motivo` de máquina; su cuerpo puede
  ser un error genérico sin filtrar internals.

## Consecuencias
### Positivas
- Mapeo completo y cerrado: ningún motivo queda sin status. El test del handler
  puede ejercer la tabla entera.
- El frontend tiene un contrato claro: status para la familia, `tipo` para el
  tono, `motivo` para el detalle.
- Códigos precisos (413/415) donde existen; 502 reintentable separado del 500 de
  bug.
### Negativas / costos
- ILEGIBLE/EXTRACCION como 422 puede dar diagnóstico engañoso si fallan los
  binarios del servidor (limitación registrada arriba).
- El híbrido 422 + `tipo: "aviso"` para SIN_VOZ exige que el frontend lea `tipo`,
  no solo el status, para dar el tono correcto. Complejidad asumida a cambio de
  no vaciar el campo `tipo`.

## Alternativas consideradas
- **SIN_VOZ = 200 + JSON**: descartada. Más RESTful en apariencia (nada falló),
  pero obligaba al cliente a distinguir dos tipos de 200 (bytes vs JSON) mirando
  Content-Type. 422 con `tipo: "aviso"` simplifica el ramificado por status sin
  perder el matiz (lo lleva `tipo`).
- **SIN_VOZ = 422 + `tipo: "error"`**: descartada. Colapsar aviso en error
  vaciaría el campo `tipo` (un solo valor posible) y trataría un silencio
  legítimo como culpa del cliente.
- **ILEGIBLE/EXTRACCION = 500**: descartada. La causa probable es el archivo del
  usuario; un 5xx mentiría al monitoreo.
- **Distinguir culpa-cliente/culpa-servidor en el dominio**: aplazada (no
  descartada). Resolvería la ambigüedad de ILEGIBLE/EXTRACCION, pero es cirugía
  en el dominio injustificada para v1.
