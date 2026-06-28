# ADR-012 — El nombre del archivo temporal no deriva del nombre enviado por el cliente

- **Estado:** Aceptada
- **Fecha:** 2026-06-27
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — capa HTTP (hardening), posterior a ADR-009/010/011.

## Contexto
El handler `POST /transcripciones` (api.py) recibe el archivo subido como
`UploadFile` y, para entregárselo al caso de uso, escribe sus bytes a un archivo
dentro de un `TemporaryDirectory`. La construcción de la ruta del temporal usaba
el nombre que envía el cliente (`file.filename`) como componente final:

```
ruta = str(Path(tmp_dir) / (file.filename or "audio"))
Path(ruta).write_bytes(contenido)
```

Una inspección de la superficie de path traversal (2026-06-27) determinó que
este es el ÚNICO vector real de la capa: `file.filename` llega CRUDO a la
construcción de ruta. Un cliente que envíe `file.filename = "../../evil.wav"`
produce `<tmp_dir>/../../evil.wav`, y el sistema operativo resuelve los `..` en
la escritura, desembocando FUERA del directorio temporal. El resto de la
superficie está cerrada: el `Content-Disposition` usa base fija anónima
(ADR-009#4), el dominio nunca recibe `file.filename` como nombre (solo la ruta
del temporal), y la extensión del cliente se usa solo para la decisión de
validación (RN-05), no para nombrar archivos.

Además, el entorno de despliegue incluye Windows, donde el conjunto de nombres
patológicos va más allá de `..`: nombres reservados (`CON`, `NUL`, `PRN`, etc.),
caracteres de control, y longitudes inválidas.

## Decisión
1. El nombre del archivo temporal NO deriva, ni total ni parcialmente, de
   `file.filename`. El nombre que envía el cliente nunca participa en la
   construcción de una ruta de filesystem.
2. El temporal se nombra con una BASE FIJA interna más la EXTENSIÓN VALIDADA. La
   extensión sale del nombre del cliente, pero SOLO tras pasar la validación de
   formato (RN-05): es uno de un conjunto cerrado y conocido (`.mp3`, `.wav`,
   `.m4a`, `.mp4`, `.mov`), no un string arbitrario. Una extensión fuera del
   conjunto se rechaza con FORMATO (415) antes de cualquier escritura, o se
   trata como entrada inválida según el flujo de validación vigente.
3. El vector queda cerrado POR CONSTRUCCIÓN, no por filtrado: como ningún
   componente controlado por el cliente entra a la ruta, no hay traversal
   posible, ni nombres reservados, ni caracteres de control, ni `..`. No se
   añade un sanitizador de nombres porque no hay nombre de cliente que sanear.

## Coherencia con decisiones previas
- **RN-02 (anonimato):** ADR-009#4 ya estableció que el nombre del archivo de
  origen —que puede llevar el nombre de un tercero, p. ej. un estudiante— no
  debe viajar de vuelta en el `Content-Disposition`. Esta decisión aplica el
  MISMO principio al temporal en disco: el nombre del usuario tampoco tiene por
  qué materializarse en el filesystem del servidor. Output anónimo y temporal
  anónimo quedan coherentes.
- **ADR-009#4:** misma estrategia (base fija anónima) extendida del output al
  temporal de entrada.

## Consecuencias
### Positivas
- El único vector de path traversal de la capa HTTP queda eliminado por
  construcción.
- Inmune a nombres patológicos de Windows (reservados, control, longitud) sin
  enumerar casos malos.
- Refuerza RN-02: el nombre del usuario no toca disco.
- El fix vive íntegramente en api.py; el dominio no cambia.
### Negativas / costos
- El temporal pierde el nombre original del usuario. Es deseable por RN-02, no
  un costo real; se registra por completitud.

## Alternativas consideradas
- **Sanear al basename (`Path(file.filename).name`)** (descartada): reduce
  `../../evil.wav` a `evil.wav`, pero mitiga por filtrado en vez de cerrar por
  construcción. Deja una cola de casos de borde (nombres reservados de Windows,
  `..` como nombre completo, caracteres de control, longitudes patológicas) que
  exigirían defensas adicionales encima. Y conserva el nombre del usuario en
  disco, erosionando el principio de RN-02 que ADR-009#4 estableció. Defensa por
  construcción es preferible a defensa por enumeración.
- **Sanitizador de nombres completo** (descartada): innecesario si el nombre del
  cliente no nombra rutas. Resuelve un problema que la decisión 1 hace
  desaparecer.

## Actualización (2026-06-27) — Realización: el handler consume el conjunto de extensiones del dominio para nombrar; no duplica la regla

### Contexto de la enmienda
Al implementar la decisión #2 ("base fija + extensión validada"), una inspección
del flujo reveló que la premisa era irrealizable como estaba escrita: la
validación de formato (RN-05) ocurre DENTRO del dominio (`validar_entrada` →
`validar_formato`), DESPUÉS de que el handler escribe el temporal. En el punto de
la escritura, el handler no dispone de una "extensión validada"; la única
información de extensión es el suffix crudo de `file.filename`. Además se
constató un problema de ORDEN: hoy el handler escribe primero (línea 90) y el
dominio valida después (línea 91), de modo que el temporal se materializa antes
de cualquier rechazo de formato.

Realizar la decisión #2 sin alterar esto admitía dos caminos defectuosos: (a)
duplicar la lista de extensiones de RN-05 en la capa HTTP —filtración de dominio
al transporte, con riesgo de divergencia—; o (b) nombre fijo sin extensión, que
rompe la clasificación del dominio (`validar_formato`/`es_video` necesitan el
suffix). Ninguno es aceptable tal cual.

### Decisión enmendada
1. El handler nombra el temporal con base fija `entrada` más un sufijo elegido a
   partir del conjunto cerrado de extensiones soportadas. Para no duplicar la
   regla, el handler IMPORTA ese conjunto desde su dueño en el dominio
   (`formato_archivo.py`), no lo re-lista. Una sola fuente de verdad: el dominio
   define el conjunto, el transporte lo consume.
2. El conjunto se usa SOLO para elegir un sufijo seguro, NO para validar. El
   handler no se convierte en punto de rechazo de formato: RN-05 sigue siendo
   del dominio, que emite FORMATO/415 como hasta ahora. Si la extensión del
   cliente pertenece al conjunto, ese literal conocido es el sufijo del temporal;
   si no pertenece, el handler usa un sufijo neutro y deja que el dominio
   rechace. La decisión de formato no se mueve al transporte; solo el dato del
   conjunto se comparte.
3. `file.filename` sigue sin participar de la construcción de la ruta: el sufijo
   proviene del conjunto del dominio (un literal de cinco posibles), no del
   string crudo del cliente. El vector de traversal queda cerrado por
   construcción, fiel a la decisión #3 original.

### Por qué esto no es la alternativa "basename" descartada
La decisión original descartó sanear al basename por mitigar-por-filtrado y
dejar cola de casos de borde. Esta enmienda NO sanea el nombre del cliente: lo
descarta y deriva el sufijo de un conjunto cerrado conocido. El nombre del
cliente no entra a la ruta ni saneado ni crudo. Se mantiene "cerrar por
construcción".

### Costo aceptado
El handler gana una dependencia de import hacia `formato_archivo.py` (el conjunto
de extensiones). Es acoplamiento transporte→dominio en la dirección correcta (el
transporte depende del dominio, no al revés) y sobre un dato que ya es público en
el dominio. No se duplica la regla; se consume.

### Nota sobre el problema de orden
Escribir-antes-de-validar se mantiene en v1: el temporal vive dentro de un
`TemporaryDirectory` que el OS controla y que se limpia al salir del context
manager (RN-12). Como el nombre del cliente ya no entra a la ruta, escribir antes
de validar no abre vector de traversal; a lo sumo escribe un archivo de formato
no soportado que el dominio rechaza acto seguido y que el temporal limpia.
Reordenar a validar-antes-de-escribir queda como mejora futura no urgente, no
requerida para cerrar el vector de seguridad.