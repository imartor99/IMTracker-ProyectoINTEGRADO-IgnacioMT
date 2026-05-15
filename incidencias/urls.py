"""
Configuración de rutas (URLs) para la aplicación de Incidencias.
Define los endpoints para autenticación, gestión de tickets y exportación de datos.
"""
# incidencias/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from .views import filtrar_incidencias, login_view, logout_view, dashboard, crear_incidencia_ajax, detalle_incidencia, editar_incidencia, borrar_incidencia, contador_no_finalizadas, obtener_incidencia, obtener_usuarios_filtros, obtener_usuarios_it, asignar_incidencia, contactar_it, exportar_csv, exportar_ticket_pdf, consultar_festivos, api_chatbot, importar_usuarios_csv

app_name = 'incidencias'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Rutas para el cambio de contraseña (usuario logueado)
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),

    # Rutas para recuperación de contraseña (usuario no logueado)
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    path('', login_required(dashboard), name='dashboard'),
    path('crear_incidencia_ajax/', login_required(crear_incidencia_ajax), name='crear_incidencia_ajax'),
    path('incidencia/<int:incidencia_id>/detalle/', detalle_incidencia, name='detalle_incidencia_ajax'),
    path('incidencia/<int:incidencia_id>/editar/', editar_incidencia, name='editar_incidencia_ajax'),
    path('borrar_incidencia/<int:id>/', borrar_incidencia, name='borrar_incidencia'),
    path('obtener_usuarios_it/', obtener_usuarios_it, name='obtener_usuarios_it'),
    path('asignar_incidencia/', asignar_incidencia, name='asignar_incidencia'),
    path('obtener_incidencia/<int:incidencia_id>/', obtener_incidencia, name='obtener_incidencia'),
    path('contador/', contador_no_finalizadas, name='contador'),
    path('filtrar_incidencias/', filtrar_incidencias, name='filtrar_incidencias'),
    path('obtener_usuarios_filtros/', obtener_usuarios_filtros, name='obtener_usuarios_filtros'),
    path('contactar_it/', login_required(contactar_it), name='contactar_it'),
    path('exportar/csv/', exportar_csv, name='exportar_csv'),
    path('incidencia/<int:incidencia_id>/pdf/', exportar_ticket_pdf, name='exportar_ticket_pdf'),
    path('api/festivos/', consultar_festivos, name='consultar_festivos'),
    path('api/chatbot/', api_chatbot, name='api_chatbot'),
    path('importar/usuarios/csv/', importar_usuarios_csv, name='importar_usuarios_csv'),
]

