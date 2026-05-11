from django.apps import AppConfig


class IncidenciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incidencias'

    def ready(self):
        # He importado el archivo signals.py para que Django registre mis eventos (como el Webhook a n8n) al arrancar.
        import incidencias.signals
