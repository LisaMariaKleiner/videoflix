from django.urls import path

from auth_app.api.views import (
    RegisterView,
    ActivateView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    PasswordResetView,
    PasswordConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password-reset'),
    path('password_confirm/<str:uidb64>/<str:token>/', PasswordConfirmView.as_view(), name='password-confirm'),
    path('activate/<str:uidb64>/<str:token>/', ActivateView.as_view(), name='activate'),
]
