LIMITE_BYTES = 1024 ** 3  # 1 GB


def validar_tamano(tamano_bytes: int) -> bool:
    return tamano_bytes <= LIMITE_BYTES
