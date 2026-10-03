from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from . import validators as v
from .models import Profile


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.CharField()
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, value):
        v.validate_username(value)
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Bu username band.")
        return value

    def validate_email(self, value):
        value = v.validate_email_format(value)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Bu email allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_phone(self, value):
        value = v.validate_phone(value)
        if Profile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
        return value

    def validate_password(self, value):
        return v.validate_password_strength(value)

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Parollar mos kelmadi."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        Profile.objects.create(user=user, phone=validated_data["phone"])
        return user


class LoginSerializer(serializers.Serializer):
    """
    'login' maydoni username, email yoki telefon raqam bo'lishi mumkin.
    Qaysi turdaligi regex orqali aniqlanadi.
    """

    login = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        login = attrs["login"].strip()
        password = attrs["password"]
        user = None

        if v.EMAIL_REGEX.match(login):
            user = User.objects.filter(email__iexact=login).first()
        elif v.PHONE_REGEX.match(v.normalize_phone(login)):
            profile = Profile.objects.select_related("user").filter(
                phone=v.normalize_phone(login)
            ).first()
            user = profile.user if profile else None
        elif v.USERNAME_REGEX.match(login):
            user = User.objects.filter(username__iexact=login).first()
        else:
            raise serializers.ValidationError(
                {"login": "Username, email yoki telefon raqam (+998901234567) kiriting."}
            )

        if user is None:
            raise serializers.ValidationError("Login yoki parol noto'g'ri.")

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError("Login yoki parol noto'g'ri.")
        if not user.is_active:
            raise serializers.ValidationError("Akkaunt faol emas.")

        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source="profile.phone", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone"]
