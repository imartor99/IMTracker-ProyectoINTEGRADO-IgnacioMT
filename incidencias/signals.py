import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Incidencia

@receiver(post_save, sender=Incidencia)
def enviar_webhook_n8n(sender, instance, created, **kwargs):
    # 'created' es True solo cuando se crea la incidencia por primera vez
    # (no queremos enviar el webhook cada vez que editemos algo)
    if created:
        # Esta URL es la que n8n usará para escuchar en su contenedor
        webhook_url = "http://imtracker_n8n:5678/webhook-test/incidencia"
        
        # Empaquetamos los datos que necesita la IA
        data = {
            "id": instance.id,
            "titulo": instance.titulo,
            "descripcion": instance.descripcion,
        }
        
        try:
            # Enviamos los datos con un timeout de 5 segundos
            requests.post(webhook_url, json=data, timeout=5)
            print(f"Webhook enviado a n8n para Incidencia #{instance.id}")
        except requests.exceptions.RequestException as e:
            # Si n8n está apagado, capturamos el error para que la app no explote
            print(f"Error al enviar webhook a n8n: {e}")
