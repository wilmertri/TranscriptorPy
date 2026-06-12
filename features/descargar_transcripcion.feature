# language: es
Característica: Descargar la transcripción
  Como una persona que ya obtuvo su transcripción
  Quiero descargarla en distintos formatos
  Para guardarla, leerla o editarla donde prefiera

  @RN-08
  Esquema del escenario: Descargar en el formato elegido
    Dado que tengo una transcripción lista
    Cuando elijo descargarla en formato "<formato>"
    Entonces obtengo un archivo "<formato>" con el texto de la transcripción
    Ejemplos:
      | formato |
      | txt     |
      | pdf     |
      | docx    |

  @RN-01 @RN-08
  Escenario: El archivo descargado conserva el texto corrido
    Dado que tengo una transcripción lista
    Cuando la descargo en cualquier formato
    Entonces el archivo contiene el texto corrido
    Y no contiene marcas de tiempo ni nombres de hablantes
