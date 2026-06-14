import math


def planificar_fragmentos(
    duracion_total: float,
    duracion_maxima: float,
) -> list[tuple[float, float]]:
    if duracion_total <= duracion_maxima:
        return [(0, duracion_total)]
    n = math.ceil(duracion_total / duracion_maxima)
    duracion_ventana = duracion_total / n
    return [(i * duracion_ventana, duracion_ventana) for i in range(n)]
