from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from auth_app.models import CustomUser

"""
This module defines the admin interface for the CustomUser model.
The CustomUserAdmin class extends the default UserAdmin to include the is_email_verified field in the list display and fieldsets.
This allows administrators to easily view and manage the email verification status of users from the Django admin panel
"""
class CustomUserAdmin(UserAdmin):
    list_display = ['email', 'username', 'is_email_verified', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Email Verification', {'fields': ('is_email_verified',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
