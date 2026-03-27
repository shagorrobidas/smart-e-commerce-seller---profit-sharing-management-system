"""User-related serializers for registration, login, listing, and profile."""

from rest_framework import serializers
from api.models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role', 'company']

    def validate_role(self, value):
        if value not in ('admin', 'staff', 'investor'):
            raise serializers.ValidationError("Role must be admin, staff, or investor.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role=validated_data.get('role', 'staff'),
            company=validated_data.get('company', ''),
        )


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'name', 'role', 'company',
            'balance', 'equity_percent', 'avatar',
            'is_active', 'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'email', 'role', 'date_joined', 'last_login']


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'company', 'balance', 'is_active', 'date_joined']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role', 'company', 'balance']

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            role=validated_data.get('role', 'staff'),
            company=validated_data.get('company', ''),
            balance=validated_data.get('balance', 0),
        )
