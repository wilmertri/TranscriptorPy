LIMITE_SEGUNDOS = 60 * 60  # 60 minutos


def validar_duracion(duracion_segundos: float) -> bool:
    return duracion_segundos <= LIMITE_SEGUNDOS
