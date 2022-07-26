from rest_framework import serializers

from .models import Level, UserRole


class LevelSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Level
        exclude = ("description",)

    def get_slug(self, obj):
        return obj.get_name_display()


class UserRoleSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserRole
        fields = ["id", "role", "user"]
