from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UsuarioPersonalizado(AbstractUser):
    """
    Extiende el modelo de usuario por defecto de Django para incluir el campo departamento.
    """
    DEPARTAMENTOS = (
        ('compras', 'Compras'),
        ('ventas', 'Ventas'),
        ('it', 'IT'),
        ('manager', 'Manager IT'),
    )
    departamento = models.CharField(max_length=20, choices=DEPARTAMENTOS, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class Incidencia(models.Model):
    """
    Representa un ticket de soporte en el sistema.
    Almacena información sobre el título, descripción, prioridad, estado y personal involucrado.
    Incluye campos para análisis automático mediante IA.
    """
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('en_curso', 'En curso'),
        ('faltan_datos', 'Faltan datos'),
        ('testing', 'Testing'),
        ('finalizada', 'Finalizada'),
    )

    PRIORIDADES = (
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    )

    titulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200)
    prioridad = models.CharField(max_length=10, choices=PRIORIDADES)
    imagen = models.ImageField(upload_to='capturas/', null=True, blank=True)
    creador = models.ForeignKey(UsuarioPersonalizado, related_name='incidencias_creadas', on_delete=models.CASCADE)
    asignado_a = models.ForeignKey(UsuarioPersonalizado, null=True, blank=True, related_name='incidencias_asignadas', on_delete=models.SET_NULL)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_asignacion = models.DateTimeField(null=True, blank=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    oculta = models.BooleanField(default=False)  # Para el borrado "no destructivo"

    # Campos IA (n8n)
    resumen_ia = models.TextField(null=True, blank=True)
    prioridad_sugerida_ia = models.CharField(max_length=10, choices=PRIORIDADES, null=True, blank=True)
    def __str__(self):
        return f"#{self.id} - {self.titulo}"
    

class Observacion(models.Model):
    """
    Permite añadir comentarios u observaciones adicionales a una incidencia específica.
    """
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name='observaciones')
    autor = models.ForeignKey(UsuarioPersonalizado, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Obs. #{self.id} para Incidencia #{self.incidencia.id}"