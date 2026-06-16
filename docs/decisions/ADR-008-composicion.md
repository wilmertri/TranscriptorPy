# ADR-008 — Composición: caso de uso y exportación por separado; factory pura, independiente de FastAPI

- **Estado:** Aceptada
- **Fecha:** 2026-06-15
- **Decisores:** Fabian.
- **Fase:** Fase 3/4 — composition root.

## Contexto
El núcleo de dominio está completo: CasoDeUsoTranscripcion (cuatro puertos) y los tres
exportadores con su selector (seleccionar_exportador / FormatoSalida). Falta ensamblar:
(1) construir el caso de uso con los adaptadores reales (MetadataFfprobe, AudioFfmpeg,
MotorOpenAI envuelto en MotorConFragmentacion, FuenteYoutubeYtdlp) y (2) fijar cómo se
relaciona la exportación con el caso de uso. La capa HTTP (FastAPI) no existe aún y no
se adelanta.

## Decisión
1. La EXPORTACIÓN vive FUERA del caso de uso. CasoDeUsoTranscripcion produce texto
   (audio/URL → texto) y conserva sus cuatro puertos; NO recibe un quinto puerto de
   exportación ni conoce el formato pedido. La exportación (seleccionar_exportador +
   exportar) es una operación posterior, con el texto ya producido.
2. El ensamblado es una FACTORY PURA en módulo propio (composicion.py), independiente
   de FastAPI: construir_caso_de_uso(config) -> CasoDeUsoTranscripcion. FastAPI, cuando
   exista, solo la llamará.
3. La factory recibe CONFIG EXPLÍCITA (un dataclass), no lee variables de entorno por
   dentro. Leer el entorno es responsabilidad de quien la llama. Así es testeable sin
   entorno ni secretos reales.
4. Reúso de colaboradores: la factory construye MetadataFfprobe y AudioFfmpeg UNA vez y
   los pasa tanto a MotorConFragmentacion (que los necesita para duración y recorte,
   ADR-006) como al caso de uso. Mismas instancias.
5. El grafo se valida con un TEST DE ESTRUCTURA (unitario, sin I/O): que la factory
   devuelva el caso de uso con los puertos del tipo correcto y, en particular, que el
   motor sea MotorConFragmentacion envolviendo a MotorOpenAI. Construir el grafo no
   ejercita los adaptadores (no hacen I/O en __init__). Un test de humo de extremo a
   extremo queda PREVISTO pero diferido: los tres tests de red existentes ya cubren cada
   adaptador por separado; su costo (red, dinero, lentitud) se justifica mejor junto a
   la capa HTTP.

## Consecuencias
### Positivas
- Separa producir-texto de serializar-a-formato: dos responsabilidades, dos tiempos.
- El caso de uso queda intacto, sin acoplarse al formato de salida.
- Factory testeable sin servidor ni secretos.
- El test de estructura ataja el error de cableado más probable (no envolver el motor,
  o duplicar metadata/audio en vez de reusarlos) a costo cero.
### Negativas / costos
- Acoplamiento temporal: quien orquesta llama primero al caso de uso y luego a la
  exportación. Aceptado: refleja el flujo real (el usuario elige formato al descargar).
- El test de estructura no prueba que el grafo FUNCIONE de punta a punta, solo que está
  bien cableado. El humo diferido cubrirá eso.

## Alternativas consideradas
- Exportador como quinto puerto del caso de uso (descartada): mezcla transcribir con
  serializar y obliga a conocer el formato antes de transcribir; no refleja el flujo.
- Factory que lee el entorno por dentro (descartada): la amarra a una fuente de config
  y la vuelve intesteable sin variables de entorno.
- Cablear dentro de FastAPI (descartada): adelanta la capa HTTP y vuelve el grafo no
  testeable sin levantar el servidor.
- Validar solo con humo de red (descartada por ahora): lento, cuesta dinero y duplica
  lo que los tests de red por adaptador ya cubren; el de estructura ataja el error
  probable a costo cero.