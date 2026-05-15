from django.test import TestCase
from django.urls import reverse
from .models import UsuarioPersonalizado, Incidencia

class IncidenciasTests(TestCase):
    def setUp(self):
        """Configuración inicial para los tests."""
        self.user = UsuarioPersonalizado.objects.create_user(
            username='testuser', 
            password='password123',
            departamento='ventas'
        )

    def test_login_page_status_code(self):
        """Verifica que la página de login carga correctamente."""
        response = self.client.get(reverse('incidencias:login'))
        self.assertEqual(response.status_code, 200)

    def test_creacion_incidencia(self):
        """Verifica que una incidencia se guarda correctamente en la base de datos."""
        incidencia = Incidencia.objects.create(
            titulo="Test Incidencia",
            descripcion="Descripción de prueba",
            prioridad="alta",
            creador=self.user
        )
        self.assertEqual(Incidencia.objects.count(), 1)
        self.assertEqual(incidencia.titulo, "Test Incidencia")
