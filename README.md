# IMTracker - Sistema de Gestión de Incidencias

**IMTracker** es una aplicación web diseñada para facilitar la creación, gestión y seguimiento de incidencias de IT. Este proyecto está siendo desarrollado como Trabajo de Fin de Grado (TFG) para el ciclo de 2º DAW.

## Características Principales (Fase 3 Completada)

El proyecto se encuentra actualmente estable y cuenta con las siguientes funcionalidades operativas:

* **Panel de Control (Dashboard):** Interfaz moderna y responsiva basada en DataTables, que permite la visualización rápida de todas las incidencias.
* **Gestión de Incidencias (CRUD):** Creación, lectura, actualización y borrado seguro de tickets.
* **Sistema de Roles y Asignaciones:** Posibilidad de asignar incidencias a usuarios específicos del departamento de IT.
* **Filtros Avanzados:** Filtrado de tickets en tiempo real por estado (Pendiente, En curso, Resuelta) y por usuario asignado.
* **Soporte Bilingüe (i18n):** Interfaz totalmente traducida al Español y al Inglés, incluyendo un selector de idioma en la pantalla de Login y traducciones dinámicas en JavaScript.
* **Generación de PDF:** Exportación directa de los detalles de cualquier incidencia a un documento PDF descargable.
* **Arquitectura de Código Limpio:** Estructura modular tanto en la parte de estilos (CSS) como en el comportamiento del cliente (Vanilla JavaScript y encapsulación de eventos).

## Stack Tecnológico

* **Backend:** Python, Django (Manejo de vistas, modelos, y autenticación).
* **Frontend:** HTML5, CSS3 (Custom Variables, Flexbox/Grid, Animaciones), JavaScript (ES6+, DOMContentLoaded).
* **Librerías Extra:** jQuery (estrictamente para peticiones AJAX y DataTables), DataTables, Bootstrap Icons.

## Estructura del Proyecto

El proyecto sigue la estructura estándar de una aplicación de Django, destacando:
* `incidencias/views.py`: Lógica principal del servidor y endpoints AJAX.
* `incidencias/static/js/dashboard.js`: Controlador principal de la vista, refactorizado siguiendo el principio de Responsabilidad Única.
* `incidencias/static/css/`: Hojas de estilo modulares (`dashboard.css`, `login.css`, etc.) sin dependencias de frameworks CSS pesados.

## Próximos Pasos (Fase 4)

El proyecto sigue en desarrollo. Las futuras implementaciones incluirán:
* **Integración con IA (n8n):** Automatización para leer el cuerpo de las incidencias, generar resúmenes automáticos y sugerir prioridades usando un modelo de lenguaje (LLM).
* **Refinamiento de UI/UX.**
* **Despliegue final.**

---
*Nota: Este README es un documento vivo y se ampliará con instrucciones de instalación y detalles técnicos exhaustivos cuando el proyecto alcance su fase final.*
