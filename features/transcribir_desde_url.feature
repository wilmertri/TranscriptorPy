# language: es
Característica: Transcribir desde una URL de YouTube
  Como una persona que quiere leer rápido lo dicho en un video de YouTube
  Quiero pegar el enlace del video y recibir su texto
  Para no tener que verlo completo

  @RN-09 @RN-04
  Escenario: Transcribir un video de YouTube válido
    Dado que tengo la URL de un video público de YouTube
    Cuando la pego en la aplicación
    Entonces el sistema obtiene el contenido desde YouTube
    Y obtengo la transcripción como texto corrido

  @RN-09
  Escenario: Rechazar una URL que no es de YouTube
    Dado que tengo la URL de un video de otra plataforma
    Cuando la pego en la aplicación
    Entonces el sistema la rechaza
    Y me indica que en esta versión solo se admiten URLs de YouTube

  @RN-11
  Escenario: Manejar una URL inválida o inaccesible
    Dado que tengo una URL de YouTube que no existe o es privada
    Cuando la pego en la aplicación
    Entonces el sistema me muestra un error claro
    Y no intenta transcribir

  @RN-07
  Escenario: Rechazar un video de YouTube que excede la duración máxima
    Dado que tengo la URL de un video de YouTube de 90 minutos
    Cuando la pego en la aplicación
    Entonces el sistema lo rechaza
    Y me indica que supera el límite de 60 minutos
