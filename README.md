# IMTracker - Sistema de Gestión de Incidencias

**IMTracker** es una aplicación web diseñada para facilitar la creación, gestión y seguimiento de incidencias de IT. Este proyecto está siendo desarrollado como Trabajo de Fin de Grado (TFG) para el ciclo de 2º DAW.

## Características Principales 

El proyecto se encuentra actualmente estable y cuenta con las siguientes funcionalidades operativas:

* **Panel de Control (Dashboard):** Interfaz moderna y responsiva basada en DataTables, que permite la visualización rápida de todas las incidencias.
* **Gestión de Incidencias (CRUD):** Creación, lectura, actualización y borrado seguro de tickets.
* **Sistema de Roles y Asignaciones:** Posibilidad de asignar incidencias a usuarios específicos del departamento de IT.
* **Filtros Avanzados:** Filtrado de tickets en tiempo real por estado (Pendiente, En curso, Resuelta) y por usuario asignado.
* **Soporte Bilingüe (i18n):** Interfaz totalmente traducida al Español y al Inglés, incluyendo un selector de idioma en la pantalla de Login y traducciones dinámicas en JavaScript.
* **Importación Masiva de Usuarios (CSV):** Herramienta administrativa para poblar la base de datos de usuarios de forma masiva mediante archivos CSV, asignando automáticamente departamentos y contraseñas de seguridad.
* **Sistema de Seguridad de Contraseñas:** Interfaz personalizada y robusta para que los nuevos usuarios puedan cambiar su contraseña predeterminada por una privada, utilizando el motor de encriptación nativo de Django.
* **Integración con IA (Chatbot IT):** Sistema de asistencia inteligente basado en **Ollama** que analiza el historial de incidencias para sugerir soluciones técnicas y responder dudas sobre el sistema en tiempo real.
* **Monitorización y Auditoría (Logs):** Sistema de trazabilidad completo que registra cada evento crítico del servidor en ficheros físicos para auditorías de seguridad.
* **Sistema de Notificaciones por Email (SMTP):** Integración con Gmail para el envío de correos reales. El sistema notifica automáticamente a los técnicos de IT cuando los usuarios envían sugerencias de mejora.
* **Recuperación de Contraseña:** Flujo completo y seguro de "Olvidé mi contraseña" que permite a los usuarios restablecer sus credenciales mediante un enlace único enviado a su correo electrónico.

## Stack Tecnológico

* **Backend:** Python, Django (Manejo de vistas, modelos, y autenticación).
* **Comunicaciones:** SMTP (Gmail) para notificaciones y recuperación de cuentas.
* **Frontend:** HTML5, CSS3, **Tailwind CSS** (generación de utilidades mediante CLI), **Vanilla JavaScript** (arquitectura estructurada y modular).
* **IA:** Ollama (Modelos de lenguaje locales para el Chatbot).
* **Librerías Extra:** jQuery (soporte para DataTables y AJAX), WeasyPrint (Generación de PDFs), DataTables, Bootstrap Icons.

## Sistema de Logs y Auditoría

Para cumplir con los estándares de seguridad y administración, la aplicación implementa un sistema de logging estructurado en tres niveles:

1.  **`django_security.log`**: Registra auditorías de acceso (Login exitoso, Login fallido con IP, Logout, Importación de usuarios). Utiliza *Django Signals* para garantizar que se capturen eventos incluso si ocurren fuera de las vistas personalizadas.
2.  **`django_general.log`**: Captura errores de ejecución, excepciones en la comunicación con la IA (Ollama) o fallos en APIs externas.
3.  **`django_requests.log`**: Monitoriza la salud de la red registrando errores HTTP (404, 500) y peticiones mal formadas.

## Seguridad y Buenas Prácticas

La aplicación incorpora medidas de seguridad sólidas heredadas de Django y aplicadas de forma activa en el frontend:
* **Protección contra Inyección SQL y XSS:** Garantizada por el uso del ORM de Django y el escapado automático de las plantillas HTML.
* **Control de Acceso Basado en Roles (RBAC):** Verificación de permisos desde el backend, enviando banderas de autorización (`puede_editar`, `puede_borrar`) para renderizar de forma segura las acciones del panel.
* **Protección CSRF (Cross-Site Request Forgery):** Las operaciones asíncronas con AJAX interceptan la cookie `csrftoken` y la inyectan en las cabeceras de seguridad.

## Próximos Pasos (Fase 5)

El proyecto está en su etapa final de despliegue:
* **Configuración de CI/CD (GitHub Actions).**
* **Despliegue final en AWS EC2 con Nginx y SSL.**

---
*Nota: Este README es un documento vivo y se ampliará con instrucciones de instalación y detalles técnicos exhaustivos cuando el proyecto alcance su fase final.*
