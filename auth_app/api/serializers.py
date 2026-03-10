from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

"""
Serializer to handle user registration. 
It includes validation to ensure that the password and confirmed password match, 
and that the email is unique. The create method is overridden to create a new user 
with the provided email and password, and to set the user as inactive until they confirm their email address.
"""
class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']

    def validate(self, data):
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError(
                {'confirmed_password': 'Passwörter stimmen nicht überein.'}
            )
        return data

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Bitte überprüfe deine Eingaben und versuche es erneut.'
            )
        return value

    def create(self, validated_data):
        validated_data.pop('confirmed_password')
        password = validated_data.pop('password')
        email = validated_data['email']
        username = email.split('@')[0]

        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            is_active=False
        )
        return user
