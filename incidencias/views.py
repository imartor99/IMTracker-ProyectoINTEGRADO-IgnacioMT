"""
Vistas principales de la aplicación de Incidencias.
Maneja la lógica de negocio para el dashboard, gestión de tickets y consumo de APIs externas.
"""
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST      #asegura que una vista solo sea llamada con un método HTTP POST
from django.http import JsonResponse, HttpResponse
import csv
import io
import json
import requests as http_client  # Para consumir APIs externas (Nager.Date y Ollama)
from django.template.loader import render_to_string
from weasyprint import HTML
from .forms import LoginForm, IncidenciaForm
from .models import Incidencia, Observacion, UsuarioPersonalizado
from django.db.models import Q         #muy util para filtrar datos en funcion a múltiples criterios
from django.contrib import messages
from django.contrib.auth import get_user_model        #interactuar de forma segura con el modelo de usuario sin importar si es predeterminado o personalizado
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import get_language, gettext as _
import logging

# Instancia del logger personalizado 'incidencias' (configurado en settings.py)
logger = logging.getLogger('incidencias')
# Instancia específica para seguridad (va al fichero django_security.log)
logger_security = logging.getLogger('django.security')

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

# Login
def login_view(request):
    """
    Maneja la autenticación de usuarios mediante un formulario de login.
    Si el método es POST, valida las credenciales y redirige al dashboard.
    """
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('incidencias:dashboard')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# Logout
def logout_view(request):
    """
    Cierra la sesión del usuario actual y redirige a la página de login.
    """
    logout(request)
    return redirect('incidencias:login')

# === SEÑALES DE AUTENTICACIÓN PARA LOGS ===
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Señal que se dispara al iniciar sesión exitosamente para registrarlo en los logs de seguridad.
    """
    logger_security.info(f'LOGIN exitoso: usuario={user.username}, departamento={getattr(user, "departamento", "N/A")}')

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        logger_security.info(f'LOGOUT: usuario={user.username}')

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    ip = request.META.get('REMOTE_ADDR') if request else 'Desconocida'
    logger_security.warning(f'LOGIN fallido: usuario_intentado={credentials.get("username")}, IP={ip}')


# Vista principal DASHBOARD #
@login_required
def dashboard(request):
    """
    Vista principal del sistema. Filtra las incidencias visibles según el departamento del usuario
    y calcula el contador de incidencias pendientes para perfiles IT/Manager.
    """
    user = request.user

    if not user.departamento:
        messages.warning(request, _("No tienes un departamento asignado. Contacta con el administrador."))
        incidencias = Incidencia.objects.none()
    elif user.departamento == "manager":
        incidencias = Incidencia.objects.filter(oculta=False)
    elif user.departamento == 'ventas':
        incidencias = Incidencia.objects.filter(creador__departamento='ventas', oculta=False)
    elif user.departamento == 'compras':
        incidencias = Incidencia.objects.filter(creador__departamento='compras', oculta=False)
    elif user.departamento == 'it':
        incidencias = Incidencia.objects.filter(oculta=False)
    else:
        messages.warning(request, _("Tu departamento no tiene permisos para ver incidencias."))
        incidencias = Incidencia.objects.none()

    # Contador solo si el usuario pertenece al departamento IT o es manager de IT
    contador_no_finalizadas = None
    if request.user.is_authenticated and (request.user.departamento or '').strip().lower() in ['it', 'manager']: #esto es para que no tenga en cuenta los espacios en blanco del departamento 
        contador_no_finalizadas = Incidencia.objects.filter(oculta=False).exclude(estado='finalizada').count()

    return render(request, 'dashboard.html', {
        'incidencias': incidencias,
        'contador_no_finalizadas': contador_no_finalizadas,
    })

# Contador Incidencias no finalizadas
@login_required
def contador_no_finalizadas(request):
    """
    Calcula y retorna el número de incidencias que no han sido finalizadas.
    Soporta peticiones AJAX para actualizaciones dinámicas en la interfaz.
    """
    contador = Incidencia.objects.filter(oculta=False).exclude(estado='finalizada').count()
    
    # Si la petición es AJAX, devolvemos JSON con el contador
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':      
        return JsonResponse({'contador': contador})
    
    return JsonResponse({'error': _('Esta vista solo admite peticiones AJAX')}, status=400)
    
    # Si la quieres usar para renderizar plantilla, para pruebas, por ejemplo:
    # return render(request, 'contador.html', {'contador': contador})            #esto lo he usado para depuracion


# CREAR nueva incidencia (AJAX)  DASHBOARD #
@require_POST
@login_required
def crear_incidencia_ajax(request):
    """
    Crea una nueva incidencia a partir de los datos recibidos por POST (AJAX).
    Retorna la información de la incidencia creada en formato JSON para actualizar el DataTable.
    """
    if request.method == 'POST':
        form = IncidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            incidencia = form.save(commit=False)
            incidencia.creador = request.user
            incidencia.save()

            incidencias = Incidencia.objects.all()

            for inc in incidencias:
                
                
                puede_actualizar = request.user.departamento in ['it', 'manager']
                puede_asignar = request.user.departamento in ['it', 'manager']

                data = {
                    'id': incidencia.id,
                    'titulo': incidencia.titulo,
                    'descripcion': incidencia.descripcion,
                    'solicitante': f"{request.user.first_name} {request.user.last_name}",
                    'tecnico_asignado': _('Sin asignar'),
                    'estado': incidencia.estado,
                    'estado_display': incidencia.get_estado_display(),
                    'prioridad': incidencia.prioridad,
                    'prioridad_display': incidencia.get_prioridad_display(),
                    'puede_borrar': request.user == incidencia.creador or request.user.departamento in ['it', 'manager'],
                    'puede_actualizar': puede_actualizar,
                    'puede_asignar': puede_asignar,
                }

            return JsonResponse({'success': True, 'data': data})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        
# Visualizacion de incidencia
@login_required
def detalle_incidencia(request, incidencia_id):
    """
    Obtiene los detalles completos de una incidencia específica.
    Calcula permisos de edición y devuelve la información junto con observaciones y análisis de IA.
    """
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    puede_editar_titulo = (
        request.user == incidencia.creador or 
        getattr(request.user, 'departamento', '').lower() in ['it', 'manager']
    )
    puede_editar_descripcion = (request.user == incidencia.creador)

    puede_cambiar_estado = (request.user.departamento in ['it', 'manager'])
    puede_cambiar_prioridad = (request.user.departamento in ['it', 'manager'])

    ultima_observacion = Observacion.objects.filter(incidencia=incidencia).order_by('-fecha').first()

    data = {
        'id': incidencia.id,
        'titulo': incidencia.titulo,
        'descripcion': incidencia.descripcion,
        'usuario': f"{incidencia.creador.first_name} {incidencia.creador.last_name}",
        'estado': incidencia.estado,
        'estado_display': incidencia.get_estado_display(),
        'prioridad': incidencia.prioridad,
        'prioridad_display': incidencia.get_prioridad_display(),
        'fecha_creacion': timezone.localtime(incidencia.fecha_creacion).strftime('%Y-%m-%d %H:%M') if incidencia.fecha_creacion else '',
        'fecha_asignacion': timezone.localtime(incidencia.fecha_asignacion).strftime('%Y-%m-%d %H:%M') if incidencia.fecha_asignacion else '',
        'fecha_resolucion': timezone.localtime(incidencia.fecha_resolucion).strftime('%Y-%m-%d %H:%M') if incidencia.fecha_resolucion else '',
        'imagen_url': incidencia.imagen.url if incidencia.imagen else '',
        'puede_editar_titulo': puede_editar_titulo,
        'puede_editar_descripcion': puede_editar_descripcion,
        'puede_cambiar_estado': puede_cambiar_estado,
        'puede_cambiar_prioridad': puede_cambiar_prioridad,
        'observacion': ultima_observacion.texto if ultima_observacion else '',
        'resumen_ia': incidencia.resumen_ia if (incidencia.resumen_ia and request.user.departamento in ['it', 'manager']) else '',
        'prioridad_sugerida_ia': incidencia.prioridad_sugerida_ia if (incidencia.prioridad_sugerida_ia and request.user.departamento in ['it', 'manager']) else '',
    }

    return JsonResponse({'success': True, 'data': data})

# Editar incidencia (ACTUALIZAR) #
@require_POST
@login_required
def editar_incidencia(request, incidencia_id):
    """
    Procesa la edición de una incidencia existente.
    Verifica permisos específicos para título, descripción, estado y prioridad antes de guardar.
    """
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    departamento_usuario = getattr(request.user, 'departamento', '').lower()
    
    puede_editar_titulo = (request.user == incidencia.creador) or (departamento_usuario in ['it', 'manager'])
    puede_editar_descripcion = (request.user == incidencia.creador)
    puede_cambiar_estado = request.user.departamento in ['it', 'manager']
    puede_cambiar_prioridad = request.user.departamento in ['it', 'manager']

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')
        prioridad = request.POST.get('prioridad')
        observacion = request.POST.get('observacion', '').strip()

        # Guardamos estado anterior para comparar después
        estado_anterior = incidencia.estado
        
        if not puede_editar_titulo and (titulo != incidencia.titulo):
            return JsonResponse({'success': False, 'error': _('No tienes permiso para editar el título')})
        
        if not puede_editar_descripcion and (descripcion != incidencia.descripcion):
            return JsonResponse({'success': False, 'error': _('No tienes permiso para editar la descripción')})
        
        if not puede_cambiar_estado and (estado != incidencia.estado):
            return JsonResponse({'success': False, 'error': _('No tienes permiso para cambiar el estado')})
        
        if estado in ['faltan_datos', 'finalizada'] and not observacion:
            return JsonResponse({'success': False, 'error': _('Debes proporcionar una observación para este estado')})

        incidencia.titulo = titulo
        incidencia.descripcion = descripcion
        incidencia.estado = estado
        
        if puede_cambiar_prioridad and prioridad:
            incidencia.prioridad = prioridad

        # Fecha de resolución según cambio de estado
        if estado_anterior != 'finalizada' and estado == 'finalizada':
            incidencia.fecha_resolucion = timezone.now()
        elif estado_anterior == 'finalizada' and estado != 'finalizada':
            incidencia.fecha_resolucion = None
        
        incidencia.save()

        # Guardar observación si aplica
        if estado in ['faltan_datos', 'finalizada'] and observacion:
            Observacion.objects.create(
                incidencia=incidencia,
                autor=request.user,
                texto=observacion
            )

        # actualizar_contador = estado_anterior != 'finalizada' and estado == 'finalizada'

        # Determina si se debe actualizar el contador cuando el estado cambie
        # Ya sea de 'finalizada' a otro o de otro a 'finalizada'
        actualizar_contador = estado_anterior != estado and ('finalizada' in [estado_anterior, estado])


        # Indicamos si hay que actualizar el contador si el estado pasó a 'finalizada' o si se paso de 'finalizada' a cualquier otro estado
        actualizar_contador = False
        if estado_anterior != 'finalizada' and estado == 'finalizada':
            actualizar_contador = True

        if estado_anterior == 'finalizada' and estado != 'finalizada':
            actualizar_contador = True


        return JsonResponse({
            'success': True,
            'data': {
                'id': incidencia.id,
                'titulo': incidencia.titulo,
                'descripcion': incidencia.descripcion,
                'solicitante': incidencia.creador.get_full_name() or incidencia.creador.username,
                'tecnico_asignado': (incidencia.asignado_a.get_full_name() or incidencia.asignado_a.username) if incidencia.asignado_a else _('Sin asignar'),
                'estado': incidencia.estado,
                'estado_display': incidencia.get_estado_display(),
                'prioridad_display': incidencia.get_prioridad_display(),
                'puede_borrar': incidencia.creador == request.user or request.user.departamento in ['it', 'manager'],
                'puede_actualizar': request.user.departamento in ['it', 'manager'],
                'puede_asignar': request.user.departamento in ['it', 'manager'],
            },
            'actualizar_contador': actualizar_contador,  # NUEVO campo
        })
    
    return JsonResponse({'success': False, 'error': _('Método no permitido')}) 

# BORRAR incidencia DASHBOARD #

@require_POST
@login_required
def borrar_incidencia(request, id):
    """
    Marca una incidencia como oculta en lugar de eliminarla físicamente.
    Solo el creador o personal de IT/Manager pueden realizar esta acción.
    """
    incidencia = get_object_or_404(Incidencia, id=id)

    if request.user == incidencia.creador or request.user.departamento in ['it', 'manager']:
        incidencia.oculta = True
        incidencia.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': _('No autorizado')}, status=403)


# ASIGNAR Incidencias #

# Vista para obtener usuarios IT con sus datos para ASIGNAR

User = get_user_model()

@login_required
def obtener_usuarios_it(request):
    """
    Retorna una lista de usuarios del departamento IT disponibles para asignación.
    Los permisos varían si el solicitante es Manager (ve a todos) o Técnico (solo a sí mismo).
    """
    user = request.user
    departamento = user.departamento.lower() if user.departamento else ''

    if departamento in ['it', 'manager']:
        if departamento == 'manager':
            # El manager puede ver a todos los usuarios de IT y a sí mismo
            usuarios_it = UsuarioPersonalizado.objects.filter(Q(departamento='it') | Q(id=user.id)).values('id', 'first_name', 'last_name')
        else:
            # Miembro normal de IT solo se puede asignar a sí mismo
            usuarios_it = UsuarioPersonalizado.objects.filter(id=user.id).values('id', 'first_name', 'last_name')

        return JsonResponse({'usuarios': list(usuarios_it)})

    # Otros departamentos no tienen permiso
    return JsonResponse({'usuarios': []})

# Obtener asignado_a de incidencias
@login_required
def obtener_incidencia(request, incidencia_id):
    """
    Obtiene el nombre del usuario asignado actualmente a una incidencia.
    """
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    asignado = incidencia.asignado_a

    if asignado:
        nombre = f"{asignado.first_name} {asignado.last_name}".strip()
        if not nombre:
            nombre = asignado.username
    else:
        nombre = None

    return JsonResponse({'success': True, 'asignado_a': nombre})


@login_required
@require_POST
def asignar_incidencia(request):
    """
    Asigna una incidencia a un técnico de IT. 
    Cambia automáticamente el estado de la incidencia a 'En curso'.
    """
    incidencia_id = request.POST.get('incidencia_id')
    usuario_id = request.POST.get('usuario_id')

    user = request.user
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    try:
        usuario_asignado = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': _('Usuario no encontrado.')})

    # Verificar permisos
    if user.departamento == 'manager':
        if usuario_asignado.departamento in ['it', 'manager']:
            incidencia.asignado_a = usuario_asignado
        else:
            return JsonResponse({'success': False, 'error': _('Solo puedes asignar a personal de IT.')})

    elif user.departamento == 'it':
        if user.id == usuario_asignado.id:
            incidencia.asignado_a = usuario_asignado
        else:
            return JsonResponse({'success': False, 'error': _('Solo puedes asignarte a ti mismo.')})
            
    else:
        return JsonResponse({'success': False, 'error': _('No tienes permisos para asignar incidencias.')})

    incidencia.fecha_asignacion = timezone.now()

    # Cambio automático de estado si no estaba en curso
    if incidencia.estado != 'en_curso':
        incidencia.estado = 'en_curso'

    incidencia.save()

    return JsonResponse({
        'success': True,
        'data': {
            'id': incidencia.id,
            'titulo': incidencia.titulo,
            'descripcion': incidencia.descripcion,
            'solicitante': incidencia.creador.get_full_name() or incidencia.creador.username,
            'tecnico_asignado': (incidencia.asignado_a.get_full_name() or incidencia.asignado_a.username) if incidencia.asignado_a else _('Sin asignar'),
            'estado': incidencia.estado,
            'estado_display': incidencia.get_estado_display(),
            'prioridad_display': incidencia.get_prioridad_display(),
            'puede_borrar': request.user.departamento in ['it', 'manager'],
            'puede_actualizar': request.user.departamento in ['it', 'manager'],
            'puede_asignar': request.user.departamento in ['it', 'manager'],
        }
    })


# FILTROS Incidencias
@login_required
def filtrar_incidencias(request):
    """
    Filtra las incidencias en base a estado, técnicos asignados y permisos de departamento.
    Retorna los resultados en formato JSON para el DataTable del dashboard.
    """
    estados = request.GET.getlist('estados')
    usuarios_ids = request.GET.getlist('usuarios')
    usuario = request.user

    # Nos quedamos solo con las que no se han borrado en el Datatable(ocultas false en BD)
    incidencias = Incidencia.objects.filter(oculta=False)

    if estados:
        incidencias = incidencias.filter(estado__in=estados)

    if usuarios_ids:
        # Filtramos estrictamente por el técnico que tiene la incidencia asignada
        incidencias = incidencias.filter(asignado_a__id__in=usuarios_ids)

    # Si no es de IT ni manager, mostrar solo las incidencias de su departamento
    if request.user.departamento not in ['it', 'manager']:
        incidencias = incidencias.filter(creador__departamento=request.user.departamento)

    data = []
    for inc in incidencias:
        # ... (lógica de permisos igual) ...
        puede_borrar = (
            request.user.departamento in ['it', 'manager'] or
            (inc.estado == 'pendiente' and request.user == inc.creador)
        )
        puede_actualizar = request.user.departamento in ['it', 'manager']
        puede_asignar = request.user.departamento in ['it', 'manager']

        data.append({
            'id': inc.id,
            'titulo': inc.titulo,
            'descripcion': inc.descripcion,
            'solicitante': inc.creador.get_full_name() or inc.creador.username,
            'tecnico_asignado': (inc.asignado_a.get_full_name() or inc.asignado_a.username) if inc.asignado_a else _('Sin asignar'),
            'estado_display': inc.get_estado_display(),
            'prioridad_display': inc.get_prioridad_display(),
            'puede_borrar': puede_borrar,
            'puede_actualizar': puede_actualizar,
            'puede_asignar': puede_asignar,
        })

    return JsonResponse({'success': True, 'incidencias': data})

# Vista para obtener usuarios IT pero para FILTROS que tiene otras condiciones
@login_required
def obtener_usuarios_filtros(request):
    """
    Retorna los técnicos de IT disponibles para ser seleccionados en los filtros del dashboard.
    """
    user = request.user
    departamento = user.departamento.lower() if user.departamento else ''

    if departamento in ['it', 'manager']:
        usuarios_it = UsuarioPersonalizado.objects.filter(Q(departamento='it')| Q(departamento='manager') | Q(id=user.id)).values('id', 'first_name', 'last_name')
    
        
        return JsonResponse({'usuarios': list(usuarios_it)})

    # Otros departamentos no tienen permiso
    return JsonResponse({'usuarios': []})


# Contactar IT (envío de email desde usuarios no-IT)
@login_required
@require_POST
def contactar_it(request):
    """
    Gestiona el envío de correos electrónicos desde usuarios no-IT hacia el equipo de soporte.
    Utiliza el sistema de mensajería de Django para notificar sugerencias o incidencias críticas.
    """
    asunto = request.POST.get('asunto', '').strip()
    mensaje = request.POST.get('mensaje', '').strip()

    if not asunto or not mensaje:
        return JsonResponse({'success': False, 'error': _('Asunto y mensaje son obligatorios.')})

    # Obtener emails de usuarios IT y Manager
    usuarios_it = UsuarioPersonalizado.objects.filter(
        Q(departamento='it') | Q(departamento='manager')
    ).exclude(email='').values_list('email', flat=True)

    destinatarios = list(usuarios_it)

    if not destinatarios:
        return JsonResponse({'success': False, 'error': _('No hay usuarios IT con email registrado.')})

    # Componer email
    remitente_nombre = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
    remitente_depto = request.user.departamento or 'Sin departamento'

    cuerpo = (
        f"Sugerencia de mejora de: {remitente_nombre}\n"
        f"Departamento: {remitente_depto}\n"
        f"Email: {request.user.email}\n"
        f"{'=' * 40}\n\n"
        f"{mensaje}"
    )

    try:
        send_mail(
            subject=f"[IMTracker - Sugerencia] {asunto}",
            message=cuerpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios,
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error al enviar el correo: {str(e)}'})

# --- GENERACION DE PDFs Y CSV --- 

@login_required
def exportar_csv(request):
    """
    Genera un archivo CSV con todas las incidencias registradas en el sistema.
    Incluye detalles de ID, estado, prioridad y fechas para análisis externo.
    """
    # Preparamos la respuesta HTTP para que el navegador descargue un archivo CSV
    response = HttpResponse(content_type='text/csv')
    
    # Añadimos la fecha actual al nombre del archivo
    fecha_actual = timezone.now().strftime("%Y%m%d")
    response['Content-Disposition'] = f'attachment; filename="incidencias_{fecha_actual}.csv"'

    # Creamos el escritor de CSV, usando punto y coma para que Excel lo abra bien
    writer = csv.writer(response, delimiter=';')

    # Escribimos los encabezados de las columnas
    writer.writerow(['ID', 'Titulo', 'Descripcion', 'Estado', 'Prioridad', 'Departamento', 'Usuario Creador', 'Asignado A', 'Fecha Creacion', 'Fecha Resolucion'])

    # Obtenemos las incidencias ordenadas por fecha
    incidencias = Incidencia.objects.all().order_by('-fecha_creacion')

    # Recorremos cada incidencia y escribimos una fila
    for inc in incidencias:
        writer.writerow([
            inc.id,
            inc.titulo,
            inc.descripcion,
            inc.get_estado_display(),
            inc.get_prioridad_display(),
            inc.creador.departamento if hasattr(inc, 'creador') and inc.creador else 'Sin asignar',
            inc.creador.username if hasattr(inc, 'creador') and inc.creador else 'Desconocido',
            inc.asignado_a.username if inc.asignado_a else 'Sin asignar',
            inc.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if inc.fecha_creacion else '',
            inc.fecha_resolucion.strftime("%Y-%m-%d %H:%M:%S") if inc.fecha_resolucion else 'No resuelta'
        ])

    logger.info(f'EXPORTAR CSV: usuario={request.user.username}, total_incidencias={incidencias.count()}')
    return response

@login_required
def exportar_ticket_pdf(request, incidencia_id):
    """
    Genera un documento PDF detallado de una incidencia individual.
    Utiliza WeasyPrint para renderizar una plantilla HTML como archivo PDF descargable.
    """
    # Obtenemos la incidencia por su ID
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)
    fecha_actual = timezone.now().strftime("%d/%m/%Y %H:%M")
    
    # Construimos el HTML pasándole los datos de la incidencia a la plantilla
    html_string = render_to_string('ticket_pdf.html', {
        'incidencia': incidencia,
        'fecha_impresion': fecha_actual
    })
    
    # Preparamos la respuesta HTTP configurada para devolver un PDF
    response = HttpResponse(content_type='application/pdf')
    nombre_archivo = f'ticket_incidencia_{incidencia.id}.pdf'
    
    # "attachment" hace que se descargue automáticamente. "inline" lo muestra en el navegador.
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'
    
    # Usamos WeasyPrint para convertir el HTML en un PDF
    HTML(string=html_string).write_pdf(response)
    
    logger.info(f'EXPORTAR PDF: usuario={request.user.username}, incidencia_id={incidencia.id}')
    return response


# API de Festivos (Consumo de API externa Nager.Date)
@login_required
def consultar_festivos(request):
    """
    Consume la API pública Nager.Date para identificar festivos nacionales en España.
    Actualiza el dashboard con información sobre el estado festivo actual y próximos eventos.
    """
    hoy = timezone.now().date()
    anio = hoy.year
    url_api = f"https://date.nager.at/api/v3/PublicHolidays/{anio}/ES"

    try:
        respuesta = http_client.get(url_api, timeout=5)
        respuesta.raise_for_status()
        festivos = respuesta.json()
    except http_client.exceptions.RequestException:
        # Si la API externa falla, devolvemos datos vacíos para no bloquear la app
        return JsonResponse({
            'es_festivo': False,
            'nombre_festivo': None,
            'proximos_festivos': []
        })

    # Compruebo si hoy coincide con algún festivo nacional
    es_festivo = False
    nombre_festivo = None
    for f in festivos:
        if f['date'] == str(hoy):
            es_festivo = True
            nombre_festivo = f['localName']
            break

    # Filtro los próximos 3 festivos que aún no han pasado
    from datetime import date as date_class
    proximos = [
        {'fecha': f['date'], 'nombre': f['localName']}
        for f in festivos
        if date_class.fromisoformat(f['date']) > hoy
    ][:3]

    return JsonResponse({
        'es_festivo': es_festivo,
        'nombre_festivo': nombre_festivo,
        'proximos_festivos': proximos
    })

# --- API CHATBOT (OLLAMA) ---
@require_POST
@login_required
def api_chatbot(request):
    """
    Interactúa con el modelo de lenguaje Llama 3 (vía Ollama) para ofrecer soporte técnico.
    Proporciona respuestas breves y directas según el idioma detectado en la sesión.
    """
    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get('mensaje', '').strip()

        if not mensaje_usuario:
            return JsonResponse({'success': False, 'error': _('El mensaje está vacío')}, status=400)

        # Dependiendo del idioma de la página, le damos el prompt en ese idioma a la IA
        lang = get_language()
        if lang == 'en':
            prompt_sistema = (
                "You are a first-level IT support assistant for a company. "
                "Your goal is to help the user solve basic technical problems "
                "before they create a support ticket. "
                "Respond in a friendly, direct, and VERY SHORT manner (max 2-3 sentences). "
                "If you don't know the answer or it's complex, kindly suggest creating a ticket."
            )
            prompt_completo = f"{prompt_sistema}\n\nUser: {mensaje_usuario}\nIT Assistant:"
        else:
            prompt_sistema = (
                "Eres un asistente técnico de soporte IT de primer nivel para una empresa. "
                "Tu objetivo es ayudar al usuario a solucionar problemas técnicos básicos "
                "antes de que cree un ticket de soporte. "
                "Responde de manera amable, directa y MUY BREVE (máximo 2-3 frases). "
                "Si no sabes la respuesta o es complejo, sugiérele amablemente que cree un ticket. "
                "REGLA CRÍTICA: Debes responder obligatoriamente en el mismo idioma en el que el usuario te escriba su mensaje."
            )
            prompt_completo = f"{prompt_sistema}\n\nUsuario: {mensaje_usuario}\nAsistente IT:"

        # Conectar con el contenedor de Ollama
        ollama_url = "http://imtracker_ollama:11434/api/generate"
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt_completo,
            "stream": False
        }

        # Petición HTTP a Ollama con timeout de 30 segundos
        response = http_client.post(ollama_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            ollama_data = response.json()
            respuesta_ia = ollama_data.get('response', _('Lo siento, no pude generar una respuesta.'))
            return JsonResponse({'success': True, 'respuesta': respuesta_ia})
        else:
            return JsonResponse({'success': False, 'error': _('Error en el servicio de IA local')}, status=500)

    except http_client.exceptions.Timeout:
        return JsonResponse({'success': False, 'error': _('La IA está tardando demasiado en responder.')}, status=504)

    except http_client.exceptions.ConnectionError:
        # Nota: En entornos de nube (como AWS EC2 t2.micro), Ollama se desactiva 
        # para evitar el agotamiento del espacio en disco (8GB limit).
        return JsonResponse({
            'success': False, 
            'error': _('La IA está desactivada en este entorno por limitaciones de hardware (AWS). Pruébala en el entorno local con Ollama.')
        }, status=503)
    except Exception as e:
        print(f"Error en api_chatbot: {e}")
        logger.error(f'Error en api_chatbot: {e}')
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# --- IMPORTACIÓN MASIVA DE USUARIOS (CSV) ---
@login_required
@require_POST
def importar_usuarios_csv(request):
    if request.user.departamento not in ['manager', 'it']:
        return JsonResponse({'success': False, 'error': _('No tienes permisos para importar usuarios.')}, status=403)
        
    if 'archivo_csv' not in request.FILES:
        return JsonResponse({'success': False, 'error': _('No se ha proporcionado ningún archivo.')}, status=400)
        
    archivo = request.FILES['archivo_csv']
    if not archivo.name.endswith('.csv'):
        return JsonResponse({'success': False, 'error': _('El archivo debe tener formato .csv')}, status=400)
        
    try:
        # Decodificar el archivo subido
        dataset = archivo.read().decode('utf-8')
        io_string = io.StringIO(dataset)
        reader = csv.reader(io_string, delimiter=',')
        
        # Saltamos la cabecera (username, first_name, last_name, email, departamento)
        next(reader, None)
        
        User = get_user_model()
        usuarios_creados = 0
        errores = 0
        
        for fila in reader:
            if len(fila) < 5:
                errores += 1
                continue
                
            username = fila[0].strip()
            first_name = fila[1].strip()
            last_name = fila[2].strip()
            email = fila[3].strip()
            departamento = fila[4].strip().lower()
            
            if not username:
                errores += 1
                continue
                
            # Comprobamos si el usuario ya existe
            if User.objects.filter(username=username).exists():
                errores += 1
                continue
                
            # Creamos el usuario con una contraseña por defecto
            # create_user se encarga de hashear la contraseña internamente
            User.objects.create_user(
                username=username,
                email=email,
                password='ImtrackerUser123!',
                first_name=first_name,
                last_name=last_name,
                departamento=departamento if departamento in ['compras', 'ventas', 'it', 'manager'] else None
            )
            usuarios_creados += 1
            
        logger.info(f'IMPORTAR USUARIOS CSV: usuario={request.user.username}, creados={usuarios_creados}, errores={errores}')
        return JsonResponse({
            'success': True,
            'mensaje': _('Importación finalizada. {usuarios_creados} usuarios creados. {errores} filas con errores u omitidas.').format(usuarios_creados=usuarios_creados, errores=errores)
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Error procesando el archivo CSV: {str(e)}'}, status=500)

