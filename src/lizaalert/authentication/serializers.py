from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for create new user backend."""

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "phone", "full_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserIdSerialiazer(serializers.Serializer):
    id = serializers.IntegerField()


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for reset user password backend."""

    email = serializers.EmailField()
