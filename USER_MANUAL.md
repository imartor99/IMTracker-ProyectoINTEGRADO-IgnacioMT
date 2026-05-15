# Manual de Usuario - IMTracker

Bienvenido a **IMTracker**, el sistema integral para la gestión de incidencias técnicas. Este manual te guiará a través de todas las funcionalidades de la plataforma.

---

## 1. Acceso al Sistema

### 1.1 Inicio de Sesión
Para acceder, introduce tus credenciales en la pantalla de login:
*   **Usuario**: Tu nombre de usuario asignado.
*   **Contraseña**: Tu clave personal.
*   **Idioma**: Puedes cambiar entre Español e Inglés usando el selector en la parte superior derecha.

### 1.2 Cambio de Contraseña
Por seguridad, si es tu primera vez accediendo, te recomendamos cambiar tu contraseña:
1.  En el menú lateral del dashboard, haz clic en **"Cambiar contraseña"**.
2.  Introduce tu contraseña actual y la nueva clave dos veces.
3.  Recibirás una confirmación visual cuando el cambio sea exitoso.

### 1.3 Recuperación de Contraseña
Si olvidas tu clave, haz clic en **"¿Olvidaste tu contraseña?"** en la pantalla de inicio (login). Introduce tu email y recibirás un enlace seguro para restablecerla.

## 2. Roles y Permisos

El sistema se adapta a tu función dentro de la empresa. Estos son los tres niveles de acceso:

| Rol | Permisos Principales |
| :--- | :--- |
| **Usuario (Ventas/Compras)** | Control sobre sus tickets (y los de su departamento): creación, seguimiento, adjuntar imágenes, borrar tickets pendientes,descargar tickets en pdf, acceso a Asistente IA y comentarios. |
| **Técnico IT** | Todo lo anterior + Gestión global: ver todos los tickets, asignación de tickets a si mismo, cambio de estados, soporte por IA e importación/exportación de datos. |
| **Manager IT** | Todo lo anterior + Responsabilidad total sobre la infraestructura, y asignacion de tickets a el equipo técnico. |

### 2.1 ¿Qué puedo hacer como Usuario? (Ventas/Compras)
Si no perteneces al equipo de IT, tienes total autonomía para:
*   **Gestionar tus tickets**: Solo tú y el equipo de IT podéis ver vuestras incidencias. Nadie de otro departamento (ej. alguien de Compras no puede ver lo de Ventas) tendrá acceso a tu información.
*   **Aportar información**: Puedes añadir observaciones y capturas de pantalla en cualquier momento para ayudar al técnico.
*   **Sugerir mejoras**: Tienes un canal directo para proponer cambios en la app.
*   **Asistente IA Personal**: Dispones de un chatbot inteligente (robot en el menú) para resolver dudas técnicas al instante sin esperar a un técnico.
*   **Privacidad**: Puedes cambiar tu contraseña siempre que quieras para asegurar tu cuenta.

---

## 3. El Dashboard Principal

El Dashboard es tu centro de control. Aquí verás:
*   **Barra Lateral**: Acceso rápido al Dashboard, Administración (solo Managers), Sugerencias, **Asistente IT** y Cambio de Idioma.
*   **Contadores**: Resumen de tus incidencias pendientes.
*   **Tabla de Incidencias**: Listado detallado de todos los tickets abiertos.

### 3.1 Filtros y Búsqueda Inteligente
Para encontrar rápidamente lo que buscas, dispones de:
*   **Selector de Estado**: Filtra para ver solo lo que está "Pendiente", "En curso", etc.
*   **Selector de Técnico (Solo IT)**: Filtra los tickets asignados a una persona específica.
*   **Barra de Búsqueda**: Busca en tiempo real por **ID**, **Título** o **Descripción**. Solo tienes que empezar a escribir y la tabla se actualizará al instante.

---

## 4. Gestión de Incidencias

### 4.1 Crear una Nueva Incidencia
1.  Haz clic en el botón **"+ Nueva Incidencia"**.
2.  **Título**: Un resumen corto del problema (ej: "La impresora no imprime").
3.  **Descripción**: Detalla qué ocurre.
4.  **Prioridad**: Elige entre Baja, Media o Alta.
5.  **Imagen**: Puedes adjuntar una captura de pantalla del error.

### 4.2 Seguimiento y Estados
Las incidencias pasan por varios estados:
*   🟡 **Pendiente**: Registrada pero aún no asignada.
*   🔵 **En curso**: Un técnico está trabajando en ella.
*   🟠 **Testing**: La solución está siendo probada.
*   🔴 **Faltan datos**: El técnico necesita más información de tu parte.
*   🟢 **Finalizada**: Problema resuelto.

---

## 5. Funciones Especiales para Personal de IT

### 5.1 Asignación de Tickets
Si tienes permisos de IT, verás un botón **"Asignar"** en cada ticket pendiente. Puedes asignarlo a ti mismo, y si eres manager IT, a otro compañero del equipo técnico.

### 5.2 Asistente con IA (Análisis Automático para Tickets)
IMTracker utiliza Inteligencia Artificial para ayudarte:
*   **Análisis Automático**: Al abrir un ticket, la IA analiza la descripción y sugiere una prioridad y un resumen técnico.


---

## 6. Administración y Datos

### 6.1 Importación Masiva Usuarios (Personal IT)
Para añadir muchos usuarios a la vez:
1.  Ve a **"Importar Usuarios"** en el menú lateral.
2.  Sube un archivo `.csv` con las columnas: `username, first_name, last_name, email, departamento`.
3.  El sistema creará las cuentas automáticamente con la contraseña por defecto: `ImtrackerUser123!`.

### 6.2 Exportación de Datos (Personal IT)
Puedes descargar un informe detallado de todas las incidencias en formato **CSV** o generar un **Ticket PDF** individual para archivarlo.

---

## 7. Soporte y Sugerencias
Si tienes una idea para mejorar el sistema, utiliza el **Buzón de Sugerencias** en el menú lateral. Tu opinión ayuda a que IMTracker siga evolucionando.

---
*© 2026 IMTracker Team - Gestión Eficiente de Soporte Técnico*
