from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from auth_app.utils import encode_user_id, generate_activation_token


def send_activation_email(user):
    """Send activation email to newly registered user."""
    token = generate_activation_token(user)
    uidb64 = encode_user_id(user.id)

    activation_link = (
        f"{settings.BACKEND_BASE_URL}/api/activate/"
        f"{uidb64}/{token}/"
    )

    context = {
        'user': user,
        'activation_link': activation_link,
        'frontend_base_url': settings.FRONTEND_BASE_URL,
    }

    subject = 'Aktiviere dein Videoflix Konto'
    text_content = (
        f'Hallo {user.email},\n\n'
        f'Vielen Dank für die Registrierung bei Videoflix!\n'
        f'Bitte klicke auf den folgenden Link um dein Konto zu aktivieren:\n'
        f'{activation_link}\n\n'
        f'Viele Grüße,\nDas Videoflix Team'
    )
    html_content = render_to_string(
        'emails/activation_email.html',
        context
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)


def send_password_reset_email(user, token, uidb64):
    """Send password reset email to user."""
    reset_link = (
        f"{settings.FRONTEND_BASE_URL}/auth/reset-password/"
        f"{uidb64}/{token}/"
    )

    context = {
        'user': user,
        'reset_link': reset_link,
        'frontend_base_url': settings.FRONTEND_BASE_URL,
    }

    subject = 'Setze dein Videoflix Passwort zurück'
    text_content = (
        f'Hallo {user.email},\n\n'
        f'Du hast eine Anfrage zum Zurücksetzen deines Passworts gestellt.\n'
        f'Bitte klicke auf den folgenden Link um dein Passwort zu ändern:\n'
        f'{reset_link}\n\n'
        f'Dieser Link ist 24 Stunden gültig.\n\n'
        f'Viele Grüße,\nDas Videoflix Team'
    )
    html_content = render_to_string(
        'emails/password_reset_email.html',
        context
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email]
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send(fail_silently=False)
