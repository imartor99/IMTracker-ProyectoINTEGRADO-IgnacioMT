# IMTracker - Sistema de Gestión de Incidencias

**IMTracker** es una aplicación web FullStack profesional diseñada para la gestión y seguimiento de incidencias de IT. Desplegada en la nube con una arquitectura moderna de microservicios.

**Acceso a Producción:** [https://imtracker.nachodaw.com](https://imtracker.nachodaw.com)

## Objetivos y Justificación

El proyecto nace de la necesidad de **optimizar la comunicación** entre los departamentos de una empresa y el equipo de soporte técnico. Los objetivos principales son:

*   **Centralización**: Eliminar el caos de correos y llamadas, unificando todas las peticiones en un solo panel de control.
*   **Eficiencia con IA**: Reducir el tiempo de resolución mediante un chatbot inteligente que asiste al usuario antes de que el técnico intervenga.
*   **Trazabilidad**: Mantener un historial completo de cada incidencia para auditorías y mejora continua.
*   **Escalabilidad**: Construir una arquitectura moderna basada en contenedores (Docker) capaz de desplegarse en la nube (AWS) con facilidad.

---

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

* **Backend:** Python 3.13, Django 6.0 (Manejo de vistas, modelos, y autenticación) y Gunicorn (Servidor WSGI).
* **Base de Datos:** PostgreSQL 15 (Motor relacional de alto rendimiento).
* **Frontend:** HTML5, CSS3 (Vanilla CSS con arquitectura BEM), **Vanilla JavaScript** (arquitectura estructurada y modular).
* **Servidor Web & Proxy:** Nginx (Servidor de alto rendimiento para tráfico y estáticos).
* **Infraestructura:** AWS EC2 (Instancia t2.micro optimizada con 1GB SWAP).
* **Seguridad:** Certbot & Let's Encrypt (Cifrado de datos de extremo a extremo via HTTPS).
* **Contenedores:** Docker & Docker Compose (Orquestación de servicios).
* **Comunicaciones:** SMTP (Gmail) para notificaciones y recuperación de cuentas.
* **IA:** Ollama (Modelos de lenguaje locales para el Chatbot).
* **APIs Externas:** Nager.Date API para la monitorización de festivos nacionales y optimización de tiempos de respuesta técnica.
* **Librerías Extra:** jQuery (soporte para DataTables y AJAX), WeasyPrint (Generación de PDFs), DataTables, Bootstrap Icons.

## Despliegue y CI/CD

El proyecto cuenta con una canalización de **Integración y Despliegue Continuo (CI/CD)**:
* **GitHub Actions:** Automatización total del ciclo de vida. Al hacer `push` a `main`, el sistema:
    1. Se conecta vía SSH a la instancia de **AWS**.
    2. Realiza una limpieza agresiva de recursos (`docker system prune`) para optimizar el almacenamiento.
    3. Descarga las imágenes de forma serializada para proteger la estabilidad del hardware.
    4. Reconstruye el entorno, aplica migraciones y recolecta archivos estáticos automáticamente.
* **Documentación Automática:** El workflow genera documentación técnica de Python y JavaScript en cada ejecución, disponible para descarga como un archivo ZIP en la sección "Artifacts" de la pestaña "Actions" en GitHub.
* **Monitorización:** Sistema de logs físicos y comprobaciones de despliegue (Health Checks).

---
*© 2026 IMTracker Team - Gestión Eficiente de Soporte Técnico*
