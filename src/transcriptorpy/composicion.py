import ssl
from dataclasses import dataclass

import httpx
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
    ssl_cert_file: str | None = None


def construir_caso_de_uso(config: ConfigTranscripcion) -> CasoDeUsoTranscripcion:
    metadata = MetadataFfprobe()
    audio = AudioFfmpeg()
    if config.ssl_cert_file is not None:
        cliente_openai = openai.OpenAI(
            api_key=config.openai_api_key,
            http_client=httpx.Client(verify=ssl.create_default_context(cafile=config.ssl_cert_file)),
        )
    else:
        cliente_openai = openai.OpenAI(api_key=config.openai_api_key)
    motor = MotorConFragmentacion(
        motor_interno=MotorOpenAI(cliente_openai),
        puerto_metadata=metadata,
        puerto_audio=audio,
    )
    return CasoDeUsoTranscripcion(
        motor=motor,
        puerto_metadata=metadata,
        puerto_audio=audio,
        puerto_fuente=FuenteYoutubeYtdlp(),
    )
