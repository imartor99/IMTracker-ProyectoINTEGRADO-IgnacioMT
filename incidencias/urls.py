# incidencias/urls.py
from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import filtrar_incidencias, login_view, logout_view, dashboard, crear_incidencia_ajax, detalle_incidencia, editar_incidencia, borrar_incidencia, contador_no_finalizadas, obtener_incidencia, obtener_usuarios_filtros, obtener_usuarios_it, asignar_incidencia, contactar_it, exportar_csv, exportar_ticket_pdf, consultar_festivos, api_chatbot, importar_usuarios_csv

app_name = 'incidencias'

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
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

