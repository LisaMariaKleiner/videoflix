from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from auth_app.tasks import queue_activation_email

User = get_user_model()


@receiver(post_save, sender=User)
def send_activation_email_signal(sender, instance, created, **kwargs):
    """Send activation email when new user is created."""
    if created and not instance.is_email_verified:
        queue_activation_email(instance.id)
