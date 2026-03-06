from django.conf import settings
from auth_app.emails import send_activation_email, send_password_reset_email


def queue_activation_email(user_id):
    """Queue activation email task to RQ or send sync in development."""
    if 'django_rq' in settings.INSTALLED_APPS:
        import django_rq
        queue = django_rq.get_queue('default')
        queue.enqueue(
            'auth_app.tasks.send_activation_email_task',
            user_id,
            job_timeout='10m'
        )
    else:
        send_activation_email_task(user_id)


def queue_password_reset_email(user_id, token, uidb64):
    """Queue password reset email task to RQ or send sync in development."""
    if 'django_rq' in settings.INSTALLED_APPS:
        import django_rq
        queue = django_rq.get_queue('default')
        queue.enqueue(
            'auth_app.tasks.send_password_reset_email_task',
            user_id,
            token,
            uidb64,
            job_timeout='10m'
        )
    else:
        send_password_reset_email_task(user_id, token, uidb64)


def send_activation_email_task(user_id):
    """Task to send activation email in background."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        send_activation_email(user)
    except User.DoesNotExist:
        pass


def send_password_reset_email_task(user_id, token, uidb64):
    """Task to send password reset email in background."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        send_password_reset_email(user, token, uidb64)
    except User.DoesNotExist:
        pass

