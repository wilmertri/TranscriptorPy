import openai

from transcriptorpy.motor_transcripcion import ErrorTranscripcion, ResultadoTranscripcion

MODELO = "gpt-4o-mini-transcribe"


class MotorOpenAI:
    def __init__(self, cliente) -> None:
        self._cliente = cliente

    def transcribir(self, ruta_audio: str) -> ResultadoTranscripcion:
        with open(ruta_audio, "rb") as archivo:
            try:
                respuesta = self._cliente.audio.transcriptions.create(
                    model=MODELO,
                    file=archivo,
                )
            except openai.OpenAIError as exc:
                raise ErrorTranscripcion(str(exc)) from exc
        return ResultadoTranscripcion(texto=respuesta.text, idioma=None)
