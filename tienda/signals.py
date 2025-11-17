from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Orden

@receiver(post_save, sender=Orden)
def notificar_admin_nueva_orden(sender, instance, created, **kwargs):
    if created:
        try:
            send_mail(
                subject=f'Nueva orden #{instance.id}',
                message=f'Orden #{instance.id} por {instance.usuario.username}. Total: {instance.total}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception:
            pass
