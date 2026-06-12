# language: es
Característica: Transcribir desde archivo
  Como una persona que quiere leer rápido lo dicho en una grabación
  Quiero subir un archivo de audio o video y recibir su texto
  Para no tener que verlo u oírlo completo

  @RN-01 @RN-03
  Escenario: Transcribir un archivo de audio válido
    Dado que tengo un archivo de audio válido en español
    Cuando lo subo a la aplicación
    Entonces obtengo la transcripción como texto corrido
    Y el texto no contiene marcas de tiempo ni nombres de hablantes

  @RN-03
  Escenario: El idioma se detecta automáticamente
    Dado que tengo un archivo de audio válido en inglés
    Cuando lo subo a la aplicación
    Entonces el sistema detecta el idioma sin que yo lo indique
    Y obtengo la transcripción en ese idioma

  @RN-04
  Escenario: Transcribir un archivo de video válido
    Dado que tengo un archivo de video válido
    Cuando lo subo a la aplicación
    Entonces el sistema obtiene el audio del video
    Y obtengo la transcripción como texto corrido

  @RN-05
  Esquema del escenario: Rechazar formatos no soportados
    Dado que tengo un archivo con extensión "<extension>"
    Cuando intento subirlo
    Entonces el sistema lo rechaza
    Y me muestra un mensaje claro de formato no soportado
    Ejemplos:
      | extension |
      | .zip      |
      | .avi      |
      | .txt      |

  @RN-06
  Escenario: Rechazar un archivo que excede el tamaño máximo
    Dado que tengo un archivo de 1.5 GB
    Cuando intento subirlo
    Entonces el sistema lo rechaza
    Y me indica que supera el límite de 1 GB

  @RN-07
  Escenario: Rechazar contenido que excede la duración máxima
    Dado que tengo un archivo de audio de 75 minutos
    Cuando intento subirlo
    Entonces el sistema lo rechaza
    Y me indica que supera el límite de 60 minutos

  @RN-10
  Escenario: Avisar cuando no hay voz reconocible
    Dado que tengo un archivo de audio sin voz reconocible
    Cuando lo subo a la aplicación
    Entonces el sistema me avisa que no se obtuvo texto
    Y no me entrega un archivo vacío

  @RN-11
  Escenario: Manejar un fallo del motor de transcripción
    Dado que subí un archivo de audio válido
    Cuando el motor de transcripción falla durante el proceso
    Entonces el sistema me muestra un error claro
    Y puedo reintentar la transcripción
