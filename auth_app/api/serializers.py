from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


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
