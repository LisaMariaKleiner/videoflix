from django.apps import AppConfig

"""
This module defines the configuration for the auth_app Django application.
The AuthAppConfig class extends App
Config and specifies the default auto field type and the name of the application.
The ready method is overridden to import the signals module, which ensures that any signal handlers defined in
the auth_app.signals module are registered when the application is ready.
This setup allows for the proper handling of signals related to user authentication and account management within the auth_app.
"""
class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'

    def ready(self):
        import auth_app.signals

