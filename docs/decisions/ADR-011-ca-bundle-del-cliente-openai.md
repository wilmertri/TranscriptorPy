# ADR-011 — CA bundle alternativo para el cliente OpenAI

- **Estado:** Aceptada
- **Fecha:** 2026-06-26
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — completar el camino real e2e (prereq del smoke test ADR-008).

## Contexto

`construir_caso_de_uso` construye el cliente OpenAI con `openai.OpenAI(api_key=...)` sin
ningún mecanismo para configurar el CA bundle. httpx 0.28.1 (cliente HTTP interno de
la biblioteca openai) **no lee `SSL_CERT_FILE` del entorno automáticamente** —
a diferencia de `requests`—, verificado empíricamente: establecer la variable no afecta
la cadena de verificación TLS que usa httpx.

El problema lo descubrió el smoke test e2e diferido de ADR-008: en un entorno
con un proxy TLS o interceptor local con CA propio (p. ej. un antivirus que re-firma
tráfico HTTPS), el camino real de construcción falla con
`CERTIFICATE_VERIFY_FAILED` mientras los tests del motor pasaban porque inyectaban
el cliente OpenAI con el SSLContext correcto desde el `conftest` de tests.

Esta es una necesidad operativa general: cualquier despliegue corporativo o entorno
de desarrollo detrás de un proxy TLS con CA propio tiene el mismo problema.

## Decisión

1. **`ConfigTranscripcion` gana un campo de dato** `ssl_cert_file: str | None = None`.
   Es una ruta a un CA bundle PEM. `None` preserva el comportamiento por defecto de
   certifi (sin cambios para entornos sin proxy). `ConfigTranscripcion` sigue siendo
   un dataclass frozen de datos puros; no porta objetos vivos ni infraestructura.

2. **`cargar_config_desde_entorno` lee `SSL_CERT_FILE` del entorno** y lo asigna al
   nuevo campo. Sigue haciendo lo que siempre hizo: leer strings del entorno y
   construir la config. No fabrica clientes ni SSLContexts.

3. **La construcción del cliente OpenAI en `composicion.py`** usa `ssl_cert_file`
   cuando no es `None`: crea `httpx.Client(verify=ssl_cert_file)` y lo pasa como
   `http_client` a `openai.OpenAI`. Si es `None`, crea el cliente sin parámetros
   adicionales (comportamiento certifi por defecto, sin cambios).
   La preocupación SSL queda pegada al cliente OpenAI, no derramada por config
   ni factory.

## Alcance

Producción soporta únicamente un CA bundle alternativo genérico (pasar `verify` con
una ruta a un PEM estándar). Particularidades de CAs mal formados —p. ej. limpiar
`VERIFY_X509_STRICT` para un CA que no marca Basic Constraints como crítico— **no
entran en producción**: si un entorno de test las necesita, viven en el `conftest`
de ese tier de tests, no en el código de la aplicación.

## Alternativas descartadas

- **Meter un `httpx.Client` vivo en `ConfigTranscripcion`**: rompe "config = datos
  puros"; convierte la frontera en constructora de adaptadores; vuelve la config
  portadora de sockets con ciclo de vida no gestionado.
- **Leer `SSL_CERT_FILE` dentro de `construir_caso_de_uso`**: rompe la pureza de
  ADR-008; la factory dejaría de ser pura (leería entorno por dentro).
- **Leer `SSL_CERT_FILE` dentro de `construir_caso_de_uso` vía variable de módulo**:
  igual que la anterior; el entorno sigue siendo un input implícito de la factory.

## Consecuencias

### Positivas
- Habilita entornos con CA propio sin tocar la pureza de la factory ni de la config.
- Cierra el camino real e2e (prereq del smoke test diferido de ADR-008).
- Coherente con ADR-008: la factory sigue siendo pura (toma config explícita); la
  frontera sigue leyendo el entorno; la config sigue siendo datos.
- El caso `ssl_cert_file=None` (la mayoría de los entornos) no añade overhead.

### Negativas / costos
- Rama condicional en `composicion.py` que el despliegue estándar (sin proxy) no
  ejercita en producción. El test unitario la cubre; el smoke test e2e la ejercita
  en integración.
- El campo `ssl_cert_file` aparece en `ConfigTranscripcion` aunque no todos los
  entornos lo usen; es un campo opcional con default `None`, costo mínimo.
