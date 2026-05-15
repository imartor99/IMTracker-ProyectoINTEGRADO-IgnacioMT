"""
Configuración del panel de administración de Django para la aplicación de Incidencias.
Permite la gestión de usuarios, incidencias y observaciones desde la interfaz administrativa.
"""
from django.contrib import admin
from .models import UsuarioPersonalizado, Incidencia, Observacion
from django.contrib.auth.admin import UserAdmin

#Para crear usuarios desde admin
class UsuarioPersonalizadoAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("departamento",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("departamento",)}),
    )

admin.site.register(UsuarioPersonalizado, UsuarioPersonalizadoAdmin)
admin.site.register(Incidencia)
admin.site.register(Observacion)
