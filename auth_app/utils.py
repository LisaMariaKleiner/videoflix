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


def get_user_by_id_and_verify_token(user_id, token):
    """
    Retrieve user by ID and verify token. 
    Returns user if valid, None otherwise.
    """
    if user_id is None:
        return None
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    
    if not verify_activation_token(user, token):
        return None
    
    return user


def validate_password_match(password1, password2):
    """
    Validate that two passwords match.
    Returns tuple (is_valid, error_message).
    """
    if not password1 or not password2:
        return False, "Both password fields are required."
    
    if password1 != password2:
        return False, "Passwords do not match."
    
    return True, None


def reset_user_password(user, new_password):
    """Set and save new password for user."""
    user.set_password(new_password)
    user.save()
