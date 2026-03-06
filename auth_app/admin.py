from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from auth_app.models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_email_verified', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Email Verification', {'fields': ('is_email_verified',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
