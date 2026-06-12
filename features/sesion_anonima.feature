# language: es
Característica: Sesión anónima de un solo uso
  Como una persona que solo quiere su texto sin complicaciones
  Quiero usar la aplicación sin registrarme
  Para obtener mi transcripción y marcharme sin dejar rastro

  @RN-02
  Escenario: Usar la aplicación sin cuenta
    Dado que entro a la aplicación
    Cuando subo un archivo para transcribir
    Entonces no se me pide registrarme ni iniciar sesión
    Y puedo completar la transcripción de forma anónima

  @RN-02 @RN-12
  Escenario: No queda nada guardado tras cerrar la sesión
    Dado que obtuve y descargué una transcripción
    Cuando cierro la sesión
    Entonces la transcripción deja de estar disponible
    Y el sistema no conserva mi contenido

  @RN-12
  Escenario: El resultado expira tras inactividad
    Dado que tengo una transcripción lista pero no la he descargado
    Cuando pasa un periodo de inactividad
    Entonces la transcripción expira
    Y debo transcribir de nuevo si la quiero
