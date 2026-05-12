## Este proyecto corresponde a la **Fase 4 del Grupo 325**
## Equipo de Desarrollo
*   **Jasson Serrano** - Líder de Proyecto
*   **Jazmin Saavedra** - Desarrolladora
*   **Wilmar Tapias** - Desarrollador
*   ## Caracteristicas
*   *   **Gestión de Clientes:** Validación robusta de documentos (solo números), nombres (solo letras) y formato de correo electrónico mediante expresiones regulares.
*   **Categorización de Servicios:**
    *   **Salas:** Cálculo por horas y capacidad.
    *   **Equipos:** Gestión de alquiler por días con opción de depósito.
    *   **Asesorías:** Gestión de consultores y descuentos por volumen de sesiones.
*   **Procesamiento de Reservas:** Cálculo de costos en tiempo real, aplicación opcional de IVA (19%) y manejo de estados.
*   **Sistema de Logs:** Registro automático de eventos y errores en un archivo físico (`Log_eventos.log`) para auditoría.
*   **Arquitectura de Software:** Implementación de Programación Orientada a Objetos (POO) avanzada, incluyendo:
    *   Clases Abstractas y Métodos Abstractos.
    *   Encapsulamiento con `@property` y `@setter`.
    *   Manejo de Excepciones Personalizadas (`SIGError`).
## Tecnologías Utilizadas
*   **Lenguaje:** Python 3
*   **Interfaz Gráfica:** Tkinter / TTK (Theme "Clam" con personalización estética).
*   **Librerías Estándar:** `datetime`, `re` (Regular Expressions), `abc`.
