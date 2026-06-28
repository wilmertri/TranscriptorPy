/**
 * contratos.js — Diccionario motivo → copy y lógica de resolución de feedback.
 * Fuente única de verdad para las respuestas no-200 del backend.
 * Los incrementos futuros (YouTube, otros formatos) importan desde aquí.
 */

// Diccionario motivo → texto en español de Colombia, trato de usted.
// Cubre el conjunto cerrado de ADR-010: motivos de dominio y de transporte.
export const COPIA_MOTIVO = {
  // Motivos de dominio
  FORMATO:                 'El formato del archivo no está soportado. Aceptamos mp3, wav, m4a, mp4 y mov.',
  TAMANO:                  'El archivo supera el límite de 1 GB.',
  DURACION:                'El audio supera la duración máxima de 60 minutos.',
  ILEGIBLE:                'No se pudo leer el archivo. Puede estar dañado o en un formato corrupto.',
  EXTRACCION:              'No se pudo extraer el audio del archivo.',
  MOTOR:                   'El servicio de transcripción no está disponible en este momento. Intente de nuevo en unos minutos.',
  URL_INVALIDA:            'La URL no es válida. En esta versión solo aceptamos enlaces de YouTube.',
  FUENTE:                  'No se pudo acceder al contenido del enlace. Intente de nuevo en unos minutos.',
  SIN_VOZ:                 'No detectamos voz reconocible en el contenido, así que no hay texto para transcribir.',
  // Motivos de transporte
  FUENTE_AUSENTE:          'Debe subir un archivo o pegar una URL, solo una de las dos.',
  FORMATO_SALIDA_INVALIDO: 'El formato de descarga solicitado no es válido.',
}

const _TEXTO_GENERICO = 'Ocurrió un error inesperado. Por favor, intente de nuevo.'

/**
 * Resuelve el tono visual y el texto a mostrar a partir de una respuesta no-200.
 *
 * Cadena de fallback:
 *   1. COPIA_MOTIVO[cuerpo.motivo]  → texto del diccionario propio
 *   2. cuerpo.mensaje               → texto que devuelve el backend
 *   3. _TEXTO_GENERICO              → texto de último recurso
 *
 * El tono se deriva del campo `tipo` del cuerpo ('aviso' | 'error').
 * No se hardcodean motivos para determinar el tono: si el backend reclasifica
 * un motivo, el front lo sigue automáticamente.
 *
 * @param {Response} respuesta — fetch Response con status != 200
 * @returns {Promise<{tono: 'error'|'aviso', texto: string}>}
 */
export async function resolverFeedbackDeRespuesta(respuesta) {
  let tono = 'error'
  let texto = _TEXTO_GENERICO

  try {
    const cuerpo = await respuesta.json()
    tono = cuerpo.tipo === 'aviso' ? 'aviso' : 'error'
    texto = COPIA_MOTIVO[cuerpo.motivo] ?? cuerpo.mensaje ?? _TEXTO_GENERICO
  } catch {
    // La respuesta no era JSON parseable; tono error y texto genérico ya asignados.
  }

  return { tono, texto }
}
