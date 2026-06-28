<script setup>
import { ref } from 'vue'
import { resolverFeedbackDeRespuesta, COPIA_MOTIVO } from './contratos.js'

// Validación de cliente (conveniencia, no sustituto del backend).
const _EXTENSIONES_VALIDAS = new Set(['.mp3', '.wav', '.m4a', '.mp4', '.mov'])
const _LIMITE_TAMANO_BYTES = 1 * 1024 * 1024 * 1024 // 1 GB

function _validarArchivo(archivo) {
  const idx = archivo.name.lastIndexOf('.')
  const ext = idx >= 0 ? archivo.name.slice(idx).toLowerCase() : ''
  if (!_EXTENSIONES_VALIDAS.has(ext)) return COPIA_MOTIVO.FORMATO
  if (archivo.size > _LIMITE_TAMANO_BYTES) return COPIA_MOTIVO.TAMANO
  return ''
}

// --- Estado de la pantalla ---
const estado = ref('idle') // idle | enviando | exito | feedback
const modo = ref('archivo') // 'archivo' | 'url' — determina qué input se muestra
const archivoSeleccionado = ref(null)
const errorArchivo = ref('') // mensaje de validación de cliente; vacío = archivo válido
const urlYoutube = ref('')
const textoFeedback = ref('')
const tonoFeedback = ref('error') // 'error' | 'aviso' — deriva del campo tipo del backend
const arrastrandoSobre = ref(false)
const formatoSalida = ref('txt') // 'txt' | 'pdf' | 'docx' — se envía como campo formato

// --- Ciclo de etapas durante la espera ---
const etapas = [
  'Subiendo archivo…',
  'Procesando audio…',
  'Transcribiendo…',
]
const etapaActual = ref(0)
let intervaloEtapas = null

function iniciarCicloEtapas() {
  etapaActual.value = 0
  intervaloEtapas = setInterval(() => {
    etapaActual.value = (etapaActual.value + 1) % etapas.length
  }, 3000)
}

function detenerCicloEtapas() {
  if (intervaloEtapas !== null) {
    clearInterval(intervaloEtapas)
    intervaloEtapas = null
  }
}

// --- Selector de modo ---
function cambiarModo(nuevoModo) {
  if (nuevoModo === modo.value) return
  // Limpiar el input del modo que se abandona para evitar valores colgados al enviar.
  if (modo.value === 'archivo') {
    archivoSeleccionado.value = null
    errorArchivo.value = ''
  }
  if (modo.value === 'url') urlYoutube.value = ''
  modo.value = nuevoModo
}

// --- Manejo del archivo ---
function alSeleccionarArchivo(evento) {
  const archivo = evento.target.files[0]
  if (!archivo) return
  archivoSeleccionado.value = archivo
  errorArchivo.value = _validarArchivo(archivo)
}

function alSoltarArchivo(evento) {
  arrastrandoSobre.value = false
  const archivo = evento.dataTransfer?.files[0]
  if (!archivo) return
  archivoSeleccionado.value = archivo
  errorArchivo.value = _validarArchivo(archivo)
}

// --- Descarga del resultado ---
function extraerNombreDescarga(respuesta) {
  const disposicion = respuesta.headers.get('content-disposition') ?? ''
  const coincidencia = disposicion.match(/filename="([^"]+)"/)
  return coincidencia ? coincidencia[1] : `transcripcion.${formatoSalida.value}`
}

function descargarBlob(blob, nombre) {
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  document.body.removeChild(enlace)
  URL.revokeObjectURL(url)
}

// --- Acción principal ---
async function transcribir() {
  const listo = modo.value === 'archivo'
    ? !!archivoSeleccionado.value
    : urlYoutube.value.trim() !== ''
  if (!listo) return

  estado.value = 'enviando'
  textoFeedback.value = ''
  iniciarCicloEtapas()

  try {
    const cuerpo = new FormData()
    if (modo.value === 'archivo') {
      cuerpo.append('file', archivoSeleccionado.value)
    } else {
      cuerpo.append('url', urlYoutube.value.trim())
    }
    cuerpo.append('formato', formatoSalida.value)

    // Sin timeout explícito: dejamos que el navegador no corte (ADR-013).
    const respuesta = await fetch('/transcripciones', {
      method: 'POST',
      body: cuerpo,
    })

    if (respuesta.ok) {
      // 200: el cuerpo es binario → descarga directa.
      const blob = await respuesta.blob()
      descargarBlob(blob, extraerNombreDescarga(respuesta))
      estado.value = 'exito'
    } else {
      // No-200: el cuerpo es JSON { tipo, motivo, mensaje } (ADR-009/010).
      // resolverFeedbackDeRespuesta aplica el diccionario y la cadena de fallback.
      const { tono, texto } = await resolverFeedbackDeRespuesta(respuesta)
      tonoFeedback.value = tono
      textoFeedback.value = texto
      estado.value = 'feedback'
    }
  } catch {
    // Error de red (sin respuesta del servidor).
    tonoFeedback.value = 'error'
    textoFeedback.value = 'No se pudo conectar con el servidor. Verifique que esté corriendo.'
    estado.value = 'feedback'
  } finally {
    detenerCicloEtapas()
  }
}

function reiniciar() {
  estado.value = 'idle'
  archivoSeleccionado.value = null
  errorArchivo.value = ''
  urlYoutube.value = ''
  textoFeedback.value = ''
  tonoFeedback.value = 'error'
  formatoSalida.value = 'txt'
  etapaActual.value = 0
}
</script>

<template>
  <div class="pagina">
    <main class="tarjeta">
      <header class="encabezado">
        <h1 class="titulo">TranscriptorPy</h1>
        <p class="subtitulo">
          Convertí audio o video a texto. Descargá el resultado sin registrarte.
        </p>
      </header>

      <!-- Formulario de subida (estado idle) -->
      <form v-if="estado === 'idle'" class="formulario" @submit.prevent="transcribir">

        <!-- Selector de modo: Archivo / URL de YouTube -->
        <div class="selector-modo" role="tablist" aria-label="Fuente de entrada">
          <button
            type="button"
            role="tab"
            :aria-selected="modo === 'archivo'"
            class="selector-modo__opcion"
            :class="{ 'selector-modo__opcion--activa': modo === 'archivo' }"
            @click="cambiarModo('archivo')"
          >
            Archivo
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="modo === 'url'"
            class="selector-modo__opcion"
            :class="{ 'selector-modo__opcion--activa': modo === 'url' }"
            @click="cambiarModo('url')"
          >
            URL de YouTube
          </button>
        </div>

        <!-- Input modo Archivo -->
        <label
          v-if="modo === 'archivo'"
          class="zona-archivo"
          :class="{ 'zona-archivo--activa': archivoSeleccionado, 'zona-archivo--arrastrando': arrastrandoSobre }"
          @dragover.prevent="arrastrandoSobre = true"
          @dragleave.prevent="arrastrandoSobre = false"
          @drop.prevent="alSoltarArchivo"
        >
          <input
            type="file"
            accept=".mp3,.wav,.m4a,.mp4,.mov"
            class="input-archivo"
            @change="alSeleccionarArchivo"
          />
          <span v-if="!archivoSeleccionado" class="zona-archivo__indicacion">
            <span class="zona-archivo__icono">↑</span>
            <span>Hacé clic o arrastrá un archivo</span>
            <span class="zona-archivo__formatos">mp3 · wav · m4a · mp4 · mov</span>
          </span>
          <span v-else class="zona-archivo__nombre">
            {{ archivoSeleccionado.name }}
          </span>
        </label>

        <!-- Input modo URL -->
        <input
          v-else
          v-model="urlYoutube"
          type="text"
          class="input-url"
          placeholder="https://www.youtube.com/watch?v=..."
          autocomplete="off"
          spellcheck="false"
        />

        <!-- Error de validación de cliente (formato o tamaño) -->
        <div
          v-if="errorArchivo"
          class="bloque-feedback bloque-feedback--error"
          role="alert"
        >
          <p class="bloque-feedback__texto">{{ errorArchivo }}</p>
        </div>

        <!-- Selector de formato de descarga -->
        <div class="fila-formato">
          <label class="fila-formato__etiqueta" for="selector-formato">Formato</label>
          <select id="selector-formato" v-model="formatoSalida" class="selector-formato">
            <option value="txt">TXT</option>
            <option value="pdf">PDF</option>
            <option value="docx">DOCX</option>
          </select>
        </div>

        <button
          type="submit"
          class="boton-primario"
          :disabled="modo === 'archivo' ? (!archivoSeleccionado || !!errorArchivo) : !urlYoutube.trim()"
        >
          Transcribir
        </button>
      </form>

      <!-- Indicador de espera (estado enviando) -->
      <div v-else-if="estado === 'enviando'" class="espera" role="status" aria-live="polite">
        <div class="spinner" aria-hidden="true"></div>
        <p class="espera__etapa">{{ etapas[etapaActual] }}</p>
        <p class="espera__aviso">
          Los archivos largos pueden tardar varios minutos.<br />No cierres esta ventana.
        </p>
      </div>

      <!-- Éxito (estado exito) -->
      <div v-else-if="estado === 'exito'" class="resultado">
        <p class="resultado__mensaje resultado__mensaje--exito">
          ¡Listo! La descarga comenzó automáticamente.
        </p>
        <button class="boton-secundario" @click="reiniciar">
          Transcribir otro archivo
        </button>
      </div>

      <!-- Feedback (estado feedback): aviso (ámbar) o error (rojo) -->
      <div
        v-else-if="estado === 'feedback'"
        class="bloque-feedback"
        :class="`bloque-feedback--${tonoFeedback}`"
        role="alert"
      >
        <p class="bloque-feedback__texto">{{ textoFeedback }}</p>
        <button class="boton-secundario" @click="reiniciar">Volver a intentar</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Página: centra la tarjeta verticalmente */
.pagina {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

/* Tarjeta principal */
.tarjeta {
  width: 100%;
  max-width: 460px;
  background: var(--color-superficie);
  border-radius: var(--radio-lg);
  box-shadow: var(--sombra);
  padding: 2.5rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

/* Encabezado */
.encabezado {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.titulo {
  margin: 0;
  font-size: var(--escala-xl);
  font-weight: var(--peso-negrita);
  color: var(--color-texto);
  letter-spacing: -0.01em;
}

.subtitulo {
  margin: 0;
  font-size: var(--escala-sm);
  color: var(--color-texto-suave);
}

/* Formulario */
.formulario {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Selector de modo (segmented control) */
.selector-modo {
  display: flex;
  background: var(--color-fondo);
  border-radius: var(--radio);
  padding: 0.25rem;
  gap: 0.25rem;
}

.selector-modo__opcion {
  flex: 1;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: calc(var(--radio) - 2px);
  font-size: var(--escala-sm);
  font-weight: var(--peso-normal);
  color: var(--color-texto-suave);
  cursor: pointer;
  transition: background var(--transicion), color var(--transicion);
}

.selector-modo__opcion--activa {
  background: var(--color-superficie);
  color: var(--color-texto);
  font-weight: var(--peso-medio);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

/* Zona de arrastre / clic */
.zona-archivo {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 8rem;
  border: 1.5px dashed var(--color-borde);
  border-radius: var(--radio);
  cursor: pointer;
  transition: border-color var(--transicion), background var(--transicion);
  position: relative;
}

.zona-archivo:hover,
.zona-archivo--arrastrando {
  border-color: var(--color-acento);
  background: var(--color-acento-claro);
}

.zona-archivo--activa {
  border-color: var(--color-acento);
  border-style: solid;
}

/* Input de archivo oculto pero accesible por la etiqueta */
.input-archivo {
  display: none;
}

.zona-archivo__indicacion {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.375rem;
  font-size: var(--escala-sm);
  color: var(--color-texto-suave);
  text-align: center;
  padding: 1rem;
}

.zona-archivo__icono {
  font-size: 1.5rem;
  line-height: 1;
  color: var(--color-acento);
}

.zona-archivo__formatos {
  font-size: 0.8125rem;
  color: var(--color-borde-activo);
  opacity: 0.7;
  letter-spacing: 0.02em;
}

.zona-archivo__nombre {
  font-size: var(--escala-sm);
  font-weight: var(--peso-medio);
  color: var(--color-acento);
  padding: 1rem;
  word-break: break-all;
  text-align: center;
}

/* Input de URL */
.input-url {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid var(--color-borde);
  border-radius: var(--radio);
  font-size: var(--escala-sm);
  color: var(--color-texto);
  background: var(--color-superficie);
  outline: none;
  transition: border-color var(--transicion);
  box-sizing: border-box;
}

.input-url:focus {
  border-color: var(--color-acento);
}

.input-url::placeholder {
  color: var(--color-texto-suave);
  opacity: 0.7;
}

/* Selector de formato */
.fila-formato {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.fila-formato__etiqueta {
  font-size: var(--escala-sm);
  color: var(--color-texto-suave);
  flex-shrink: 0;
}

.selector-formato {
  padding: 0.375rem 0.625rem;
  border: 1.5px solid var(--color-borde);
  border-radius: var(--radio);
  font-size: var(--escala-sm);
  color: var(--color-texto);
  background: var(--color-superficie);
  cursor: pointer;
  outline: none;
  transition: border-color var(--transicion);
}

.selector-formato:focus {
  border-color: var(--color-acento);
}

/* Botones */
.boton-primario {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: var(--color-acento);
  color: #fff;
  border: none;
  border-radius: var(--radio);
  font-size: var(--escala-base);
  font-weight: var(--peso-medio);
  cursor: pointer;
  transition: background var(--transicion);
}

.boton-primario:hover:not(:disabled) {
  background: var(--color-acento-hover);
}

.boton-primario:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.boton-secundario {
  padding: 0.625rem 1.25rem;
  background: transparent;
  color: var(--color-acento);
  border: 1.5px solid var(--color-acento);
  border-radius: var(--radio);
  font-size: var(--escala-sm);
  font-weight: var(--peso-medio);
  cursor: pointer;
  transition: background var(--transicion), color var(--transicion);
}

.boton-secundario:hover {
  background: var(--color-acento);
  color: #fff;
}

/* Espera */
.espera {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
  text-align: center;
}

.spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid var(--color-borde);
  border-top-color: var(--color-acento);
  border-radius: 50%;
  animation: girar 0.9s linear infinite;
}

@keyframes girar {
  to { transform: rotate(360deg); }
}

.espera__etapa {
  margin: 0;
  font-size: var(--escala-base);
  font-weight: var(--peso-medio);
  color: var(--color-texto);
}

.espera__aviso {
  margin: 0;
  font-size: var(--escala-sm);
  color: var(--color-texto-suave);
  line-height: 1.6;
}

/* Resultado */
.resultado {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
}

.resultado__mensaje {
  margin: 0;
  font-size: var(--escala-base);
  line-height: 1.5;
}

.resultado__mensaje--exito {
  color: var(--color-texto);
}

/* Bloque de feedback: ámbar (aviso) o rojo (error) */
.bloque-feedback {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: flex-start;
  padding: 1rem 1.125rem;
  border-radius: var(--radio);
  border-left: 4px solid currentColor;
}

.bloque-feedback--error {
  color: var(--color-error);
  background: var(--color-error-fondo);
}

.bloque-feedback--aviso {
  color: var(--color-aviso);
  background: var(--color-aviso-fondo);
}

.bloque-feedback__texto {
  margin: 0;
  font-size: var(--escala-base);
  line-height: 1.5;
  color: inherit;
}
</style>
