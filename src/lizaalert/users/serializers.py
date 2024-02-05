from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from lizaalert.users.models import Badge, Department, Level, Location, UserRole, Volunteer

User = get_user_model()


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            "name",
            "description",
            "image",
            "issued_for",
        ]


class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    location = serializers.CharField(required=False, allow_null=True, source="location.region")
    full_name = serializers.CharField(source="user.full_name", allow_blank=True, required=False)
    photo = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    level = serializers.CharField(source="level_confirmed.level.name", read_only=True)
    count_pass_course = serializers.IntegerField(read_only=True)
    phone_number = serializers.CharField(source="user.phone", read_only=True)
    department = serializers.CharField(required=False, allow_null=True, source="department.title")

    class Meta:
        model = Volunteer
        fields = [
            "id",
            "photo",
            "full_name",
            "level",
            "department",
            "count_pass_course",
            "birth_date",
            "location",
            "call_sign",
            "phone_number",
            "email",
        ]

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.birth_date = validated_data.get("birth_date", instance.birth_date)
            instance.call_sign = validated_data.get("call_sign", instance.call_sign)

            location = validated_data.get("location", None)
            if location and (Location.objects.filter(region=location["region"]).exists()):
                instance.location = Location.objects.get(region=location["region"])

            department = validated_data.get("department", None)
            if department and (Department.objects.filter(title=department["title"]).exists()):
                instance.department = Department.objects.get(title=department["title"])

            full_name = validated_data.get("user", {}).get("full_name", None)
            if full_name is not None:
                instance.user.full_name = full_name
                instance.user.save()

            if validated_data.get("photo") is not None:
                instance.photo = validated_data.pop("photo")
            instance.save()
            return instance


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


class Error404Serializer(serializers.Serializer):
    detail = serializers.CharField()


class Error400Serializer(serializers.Serializer):
    error_field = serializers.ListField()
