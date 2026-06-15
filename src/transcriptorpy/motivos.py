from enum import Enum


class MotivoRechazo(str, Enum):
    FORMATO = "FORMATO"
    TAMANO = "TAMANO"
    DURACION = "DURACION"
    ILEGIBLE = "ILEGIBLE"
    EXTRACCION = "EXTRACCION"
    MOTOR = "MOTOR"
    URL_INVALIDA = "URL_INVALIDA"
    FUENTE = "FUENTE"
