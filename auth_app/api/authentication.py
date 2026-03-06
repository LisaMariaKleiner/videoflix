from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework import HTTP_HEADER_ENCODING


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads tokens from cookies
    if no Authorization header is present.
    """

    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if a valid token has been
        supplied. Otherwise returns `None`.
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header:
            try:
                return super().authenticate(request)
            except AuthenticationFailed:
                pass
        
        raw_token = request.COOKIES.get('access_token', None)
        
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

        return self.get_user(validated_token), validated_token

