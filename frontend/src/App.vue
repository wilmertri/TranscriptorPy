<script setup>
import { ref } from 'vue'

// --- Estado de la pantalla ---
const estado = ref('idle') // idle | enviando | exito | error
const archivoSeleccionado = ref(null)
const mensajeError = ref('')
const arrastrandoSobre = ref(false)

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

// --- Manejo del archivo ---
function alSeleccionarArchivo(evento) {
  const archivo = evento.target.files[0]
  if (archivo) archivoSeleccionado.value = archivo
}

function alSoltarArchivo(evento) {
  arrastrandoSobre.value = false
  const archivo = evento.dataTransfer?.files[0]
  if (archivo) archivoSeleccionado.value = archivo
}

// --- Descarga del resultado ---
function extraerNombreDescarga(respuesta) {
  const disposicion = respuesta.headers.get('content-disposition') ?? ''
  const coincidencia = disposicion.match(/filename="([^"]+)"/)
  return coincidencia ? coincidencia[1] : 'transcripcion.txt'
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
  if (!archivoSeleccionado.value) return

  estado.value = 'enviando'
  mensajeError.value = ''
  iniciarCicloEtapas()

  try {
    const cuerpo = new FormData()
    cuerpo.append('file', archivoSeleccionado.value)
    cuerpo.append('formato', 'txt')

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
      // TODO: bifurcar por respuesta.json().tipo y .motivo para mensajes
      // específicos por MotivoRechazo (FORMATO→415, TAMANO→413, MOTOR/FUENTE→502,
      // DURACION/ILEGIBLE/EXTRACCION/URL_INVALIDA→422, SIN_VOZ→422 aviso).
      // Seam: await respuesta.json() → { tipo, motivo, mensaje } → mapear a copia.
      // Por ahora, marcador de posición genérico; este bloque es el punto de
      // extensión del siguiente incremento.
      estado.value = 'error'
      mensajeError.value = 'La transcripción no pudo completarse. Intentá de nuevo.'
    }
  } catch {
    // Error de red o respuesta no procesable.
    estado.value = 'error'
    mensajeError.value = 'No se pudo conectar con el servidor. Verificá que esté corriendo.'
  } finally {
    detenerCicloEtapas()
  }
}

function reiniciar() {
  estado.value = 'idle'
  archivoSeleccionado.value = null
  mensajeError.value = ''
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
        <label
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

        <button type="submit" class="boton-primario" :disabled="!archivoSeleccionado">
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

      <!-- Error (estado error) -->
      <div v-else-if="estado === 'error'" class="resultado">
        <p class="resultado__mensaje resultado__mensaje--error">{{ mensajeError }}</p>
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

.resultado__mensaje--error {
  color: var(--color-error);
}
</style>
