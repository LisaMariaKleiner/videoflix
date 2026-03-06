from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_email_verified}"


activation_token_generator = AccountActivationTokenGenerator()


def encode_user_id(user_id):
    """Encode user ID to base64."""
    return urlsafe_base64_encode(force_bytes(str(user_id)))


def decode_user_id(uidb64):
    """Decode user ID from base64."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        return int(uid)
    except (TypeError, ValueError, OverflowError):
        return None


def generate_activation_token(user):
    """Generate activation token for user."""
    return activation_token_generator.make_token(user)


def verify_activation_token(user, token):
    """Verify activation token for user."""
    return activation_token_generator.check_token(user, token)
