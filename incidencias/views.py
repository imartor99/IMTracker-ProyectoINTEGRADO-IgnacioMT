from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST      #asegura que una vista solo sea llamada con un método HTTP POST
from django.http import JsonResponse, HttpResponse
import csv
from .forms import LoginForm, IncidenciaForm
from .models import Incidencia, Observacion, UsuarioPersonalizado
from django.db.models import Q         #muy util para filtrar datos en funcion a múltiples criterios
from django.contrib import messages
from django.contrib.auth import get_user_model        #interactuar de forma segura con el modelo de usuario sin importar si es predeterminado o personalizado
from django.core.mail import send_mail
from django.conf import settings

    
# Login
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


# Logout
def logout_view(request):
    logout(request)
    return redirect('login')


# Vista principal DASHBOARD #
@login_required
def dashboard(request):
    user = request.user

    if not user.departamento:
        messages.warning(request, "No tienes un departamento asignado. Contacta con el administrador.")  #aviso si el user no tiene departamento asignado
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
        messages.warning(request, "Tu departamento no tiene permisos para ver incidencias.")
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
    contador = Incidencia.objects.filter(oculta=False).exclude(estado='finalizada').count()
    
    # Si la petición es AJAX, devolvemos JSON con el contador
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':      
        return JsonResponse({'contador': contador})
    
    return JsonResponse({'error': 'Esta vista solo admite peticiones AJAX'}, status=400)
    
    # Si la quieres usar para renderizar plantilla, para pruebas, por ejemplo:
    # return render(request, 'contador.html', {'contador': contador})            #esto lo he usado para depuracion


# CREAR nueva incidencia (AJAX)  DASHBOARD #
@require_POST
@login_required
def crear_incidencia_ajax(request):
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
                    'usuario': f"{request.user.first_name} {request.user.last_name}",
                    'estado': incidencia.estado, #valor interno
                    'estado_display': incidencia.get_estado_display(),
                    'prioridad': incidencia.prioridad,  #valor interno
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
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    puede_editar_titulo = (
        request.user == incidencia.creador or 
        getattr(request.user, 'departamento', '').lower() in ['it', 'manager']
    )
    puede_editar_descripcion = (request.user == incidencia.creador)

    puede_cambiar_estado = (request.user.departamento in ['it', 'manager'])

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
        'fecha_creacion': incidencia.fecha_creacion.strftime('%Y-%m-%d %H:%M') if incidencia.fecha_creacion else '',
        'fecha_asignacion': incidencia.fecha_asignacion.strftime('%Y-%m-%d %H:%M') if incidencia.fecha_asignacion else '',
        'fecha_resolucion': incidencia.fecha_resolucion.strftime('%Y-%m-%d %H:%M') if incidencia.fecha_resolucion else '',
        'imagen_url': incidencia.imagen.url if incidencia.imagen else '',
        'puede_editar_titulo': puede_editar_titulo,
        'puede_editar_descripcion': puede_editar_descripcion,
        'puede_cambiar_estado': puede_cambiar_estado,
        'observacion': ultima_observacion.texto if ultima_observacion else '',
    }

    return JsonResponse({'success': True, 'data': data})

# Editar incidencia (ACTUALIZAR) #
@require_POST
@login_required
def editar_incidencia(request, incidencia_id):
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    departamento_usuario = getattr(request.user, 'departamento', '').lower()
    
    puede_editar_titulo = (request.user == incidencia.creador) or (departamento_usuario in ['it', 'manager'])
    puede_editar_descripcion = (request.user == incidencia.creador)
    puede_cambiar_estado = request.user.departamento in ['it', 'manager']

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        estado = request.POST.get('estado')
        observacion = request.POST.get('observacion', '').strip()

        # Guardamos estado anterior para comparar después
        estado_anterior = incidencia.estado
        
        if not puede_editar_titulo and (titulo != incidencia.titulo):
            return JsonResponse({'success': False, 'error': 'No tienes permiso para editar el título'})
        
        if not puede_editar_descripcion and (descripcion != incidencia.descripcion):
            return JsonResponse({'success': False, 'error': 'No tienes permiso para editar la descripción'})
        
        if not puede_cambiar_estado and (estado != incidencia.estado):
            return JsonResponse({'success': False, 'error': 'No tienes permiso para cambiar el estado'})
        
        if estado in ['faltan_datos', 'finalizada'] and not observacion:
            return JsonResponse({'success': False, 'error': 'Debes proporcionar una observación para este estado'})

        incidencia.titulo = titulo
        incidencia.descripcion = descripcion
        incidencia.estado = estado
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
                'usuario': incidencia.creador.get_full_name() or incidencia.creador.username,
                'estado': incidencia.estado,
                'estado_display': incidencia.get_estado_display(),
                'prioridad_display': incidencia.get_prioridad_display(),
                'puede_borrar': incidencia.creador == request.user or request.user.departamento in ['it', 'manager'],
            },
            'actualizar_contador': actualizar_contador,  # NUEVO campo
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'}) 

# BORRAR incidencia DASHBOARD #

@require_POST
@login_required
def borrar_incidencia(request, id):
    incidencia = get_object_or_404(Incidencia, id=id)

    if request.user == incidencia.creador or request.user.departamento in ['it', 'manager']:
        incidencia.oculta = True
        incidencia.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'No autorizado'}, status=403)


# ASIGNAR Incidencias #

# Vista para obtener usuarios IT con sus datos para ASIGNAR

User = get_user_model()

@login_required
def obtener_usuarios_it(request):
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
    incidencia_id = request.POST.get('incidencia_id')
    usuario_id = request.POST.get('usuario_id')

    user = request.user
    incidencia = get_object_or_404(Incidencia, id=incidencia_id)

    try:
        usuario_asignado = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado.'})

    # Verificar permisos
    if user.departamento == 'manager':
        if usuario_asignado.departamento in ['it', 'manager']:
            incidencia.asignado_a = usuario_asignado
        else:
            return JsonResponse({'success': False, 'error': 'Solo puedes asignar a personal de IT.'})

    elif user.departamento == 'it':
        if user.id == usuario_asignado.id:
            incidencia.asignado_a = usuario_asignado
        else:
            return JsonResponse({'success': False, 'error': 'Solo puedes asignarte a ti mismo.'})
            
    else:
        return JsonResponse({'success': False, 'error': 'No tienes permisos para asignar incidencias.'})

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
            'usuario': incidencia.creador.get_full_name() or incidencia.creador.username,
            'estado': incidencia.estado,
            'estado_display': incidencia.get_estado_display(),
            'prioridad_display': incidencia.get_prioridad_display(),
            'puede_borrar': request.user.departamento in ['it', 'manager'],
        }
    })


# FILTROS Incidencias
@login_required
def filtrar_incidencias(request):
    estado = request.GET.get('estado')
    usuarios_ids = request.GET.getlist('usuarios')
    usuario = request.user

    # Nos quedamos solo con las que no se han borrado en el Datatable(ocultas false en BD)
    incidencias = Incidencia.objects.filter(oculta=False)

    if estado:
        incidencias = incidencias.filter(estado=estado)

    if usuarios_ids:
        incidencias = incidencias.filter(asignado_a__id__in=usuarios_ids)

    # Si no es de IT ni manager, mostrar solo sus propias incidencias
    if not request.user.departamento in ['it', 'manager']:
        incidencias = incidencias.filter(creador=usuario)

    data = []
    for inc in incidencias:
        # Solo puede borrar si la incidencia está pendiente y es su creador
        puede_borrar = (
            request.user.departamento in ['it', 'manager'] or
            (inc.estado == 'pendiente' and request.user == inc.creador)
        )

        # Solo pueden ver actualizar/asignar los usuarios del dpto. IT o Manager
        puede_actualizar = request.user.departamento in ['it', 'manager']
        puede_asignar = request.user.departamento in ['it', 'manager']

        data.append({
            'id': inc.id,
            'titulo': inc.titulo,
            'descripcion': inc.descripcion,
            'usuario': inc.creador.get_full_name() or inc.creador.username,
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
    """Vista para que usuarios de otros departamentos envíen solicitudes al equipo IT por correo electrónico."""
    asunto = request.POST.get('asunto', '').strip()
    mensaje = request.POST.get('mensaje', '').strip()

    if not asunto or not mensaje:
        return JsonResponse({'success': False, 'error': 'Asunto y mensaje son obligatorios.'})

    # Obtener emails de usuarios IT y Manager
    usuarios_it = UsuarioPersonalizado.objects.filter(
        Q(departamento='it') | Q(departamento='manager')
    ).exclude(email='').values_list('email', flat=True)

    destinatarios = list(usuarios_it)

    if not destinatarios:
        return JsonResponse({'success': False, 'error': 'No hay usuarios IT con email registrado.'})

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

    return response
