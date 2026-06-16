from dataclasses import dataclass

import openai

from transcriptorpy.audio_ffmpeg import AudioFfmpeg
from transcriptorpy.fuente_youtube_ytdlp import FuenteYoutubeYtdlp
from transcriptorpy.metadata_ffprobe import MetadataFfprobe
from transcriptorpy.motor_con_fragmentacion import MotorConFragmentacion
from transcriptorpy.motor_openai import MotorOpenAI
from transcriptorpy.procesar_transcripcion import CasoDeUsoTranscripcion


@dataclass(frozen=True)
class ConfigTranscripcion:
    openai_api_key: str


def construir_caso_de_uso(config: ConfigTranscripcion) -> CasoDeUsoTranscripcion:
    metadata = MetadataFfprobe()
    audio = AudioFfmpeg()
    motor = MotorConFragmentacion(
        motor_interno=MotorOpenAI(openai.OpenAI(api_key=config.openai_api_key)),
        puerto_metadata=metadata,
        puerto_audio=audio,
    )
    return CasoDeUsoTranscripcion(
        motor=motor,
        puerto_metadata=metadata,
        puerto_audio=audio,
        puerto_fuente=FuenteYoutubeYtdlp(),
    )
