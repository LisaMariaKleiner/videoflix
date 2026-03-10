from django.contrib.auth.models import AbstractUser
from django.db import models

"""
This module defines the CustomUser model, which extends Django's AbstractUser.
It includes an email field that is unique and a boolean field to track email verification status.
The USERNAME_FIELD is set to 'email' to allow authentication using the email address instead of the username."""
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email
