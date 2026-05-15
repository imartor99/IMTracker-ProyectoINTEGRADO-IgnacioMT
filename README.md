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
* **Filtros Combinados e Inteligentes:** Sistema de búsqueda avanzado que permite la **selección múltiple** de estados y técnicos de forma simultánea, facilitando la auditoría de tickets específicos.
* **Sistema de UX Moderno (Modales):** Motor de notificaciones personalizado que sustituye las alertas nativas del navegador por modales estilizados con animaciones fluidas, mejorando la coherencia visual y la experiencia de usuario.
* **Manual de Usuario Integrado:** Documentación exhaustiva en [USER_MANUAL.md](USER_MANUAL.md) que cubre desde el primer acceso hasta las funciones avanzadas de IA.

## Stack Tecnológico

* **Backend:** Python, Django (Manejo de vistas, modelos, y autenticación).
* **Comunicaciones:** SMTP (Gmail) para notificaciones y recuperación de cuentas.
* **Frontend:** HTML5, CSS3 (Vanilla CSS con arquitectura BEM), **Vanilla JavaScript** (arquitectura estructurada y modular).
* **IA:** Ollama (Modelos de lenguaje locales para el Chatbot).
* **APIs Externas:** Nager.Date API para la monitorización de festivos nacionales y optimización de tiempos de respuesta técnica.
* **Librerías Extra:** jQuery (soporte para DataTables y AJAX), WeasyPrint (Generación de PDFs), DataTables, Bootstrap Icons.

## Despliegue y Producción

La aplicación está preparada para entornos de alta disponibilidad:
* **Dockerizado:** Contenedores aislados para Django y la base de datos, garantizando la portabilidad.
* **CI/CD:** Automatización total mediante **GitHub Actions** para el despliegue continuo en **AWS EC2**.
* **Seguridad SSL:** Configuración prevista mediante Nginx para cifrado de extremo a extremo.

---
*© 2026 IMTracker Team - Gestión Eficiente de Soporte Técnico*
