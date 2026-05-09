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
* **Frontend:** HTML5, CSS3, **Tailwind CSS** (generación de utilidades mediante CLI), JavaScript (ES6+, DOMContentLoaded).
* **Librerías Extra:** jQuery (estrictamente para peticiones AJAX y DataTables), DataTables, Bootstrap Icons.

## Estructura del Proyecto

El proyecto sigue la estructura estándar de una aplicación de Django, destacando:
* `incidencias/views.py`: Lógica principal del servidor y endpoints AJAX.
* `incidencias/static/js/dashboard.js`: Controlador principal de la vista(frontend), refactorizado siguiendo las buenas prácticas de programación, el principio de Responsabilidad Única y el enfoque MVC.
* `incidencias/static/css/`: Hojas de estilo que combinan CSS modular clásico (`dashboard.css`, `login.css`) con el framework **Tailwind CSS** (`output.css`) para agilizar el maquetado y diseño responsivo.

## Seguridad y Buenas Prácticas

La aplicación incorpora medidas de seguridad sólidas heredadas de Django y aplicadas de forma activa en el frontend:
* **Protección contra Inyección SQL y XSS:** Garantizada por el uso del ORM de Django y el escapado automático de las plantillas HTML.
* **Control de Acceso Basado en Roles (RBAC):** Verificación de permisos desde el backend, enviando banderas de autorización (`puede_editar`, `puede_borrar`) para renderizar de forma segura las acciones del panel.
* **Protección CSRF (Cross-Site Request Forgery):** Prevención contra ataques de falsificación de peticiones. Las operaciones asíncronas con AJAX interceptan la cookie `csrftoken` del usuario y la inyectan en las cabeceras de seguridad, asegurando que ninguna web de terceros pueda ejecutar acciones críticas (como borrar o asignar tickets) en nombre del usuario.

## Próximos Pasos (Fase 4)

El proyecto sigue en desarrollo. Las futuras implementaciones incluirán:
* **Integración con IA (n8n):** Automatización para leer el cuerpo de las incidencias, generar resúmenes automáticos y sugerir prioridades usando un modelo de lenguaje (LLM).
* **Refinamiento de UI/UX.**
* **Despliegue final.**

---
*Nota: Este README es un documento vivo y se ampliará con instrucciones de instalación y detalles técnicos exhaustivos cuando el proyecto alcance su fase final.*
