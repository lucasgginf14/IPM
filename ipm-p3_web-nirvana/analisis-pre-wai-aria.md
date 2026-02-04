# Análisis de los Casos de Uso

1. Buscar Paciente

    Elemento clave: Campo de texto con validación del formato XXX-XX-XXXX.
    Requisitos de accesibilidad:
        Usar aria-live para informar errores de validación al usuario en tiempo real.
        Asegurarse de que el label esté correctamente asociado al campo de texto con for.

2. Seleccionar Período de Tiempo

    Elemento clave: Menú desplegable con opciones adicionales (últimos días o rango de fechas).
    Requisitos de accesibilidad:
        Usar aria-expanded y aria-controls para indicar el estado expandido de opciones adicionales.
        Asociar dinámicamente los campos adicionales con etiquetas descriptivas.

3. Generar Informe

    Elemento clave: Validación de datos antes de generar el informe.
    Requisitos de accesibilidad:
        Anunciar errores o confirmaciones con aria-live.

4. Visualizar Informe

    Elemento clave: Mostrar datos del informe con errores destacados.
    Requisitos de accesibilidad:
        Resaltar errores significativos visualmente y a través de descripciones accesibles (aria-describedby).

# Actualización y Estados de la Interfaz

Estos son los estados principales de la interfaz y las reglas de WAI-ARIA relevantes:

  - Introducción del código de paciente:
    - Mostrar mensajes de error con aria-live="polite".
    - Asegurar que el patrón de validación esté indicado en el atributo pattern.

  - Selección de período:
     - Cambiar el atributo aria-expanded según corresponda.
     - Asociar los nuevos campos dinámicamente con aria-labelledby.

  - Generación de informe:
    - Anunciar el estado de éxito o error del informe con aria-live.

  - Visualización del informe:
     - Usar resaltados para errores (role="alert" o aria-describedby para proporcionar contexto adicional).
