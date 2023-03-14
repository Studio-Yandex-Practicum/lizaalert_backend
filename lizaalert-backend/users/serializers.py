from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Badge, Level, Location, UserRole, Volunteer

User = get_user_model()


class BageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            "name",
            "description",
        ]


class FullNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "patronymic"]

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.patronymic = validated_data.get("patronymic", instance.patronymic)
        instance.save()
        return instance


class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    location = serializers.CharField(required=False, allow_null=True, source="location.region")
    full_name = FullNameSerializer(source="user")
    photo = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)
    level = serializers.CharField(source="level_confirmed", read_only=True)
    badges = BageSerializer(many=True, read_only=True)
    count_pass_course = serializers.IntegerField(read_only=True)

    class Meta:
        model = Volunteer
        fields = [
            "id",
            "phone_number",
            "email",
            "full_name",
            "birth_date",
            "location",
            "call_sign",
            "photo",
            "level",
            "badges",
            "count_pass_course",
        ]

    @transaction.non_atomic_requests
    def update(self, instance, validated_data):
        instance.birth_date = validated_data.get("birth_date", instance.birth_date)
        instance.call_sign = validated_data.get("call_sign", instance.call_sign)
        instance.phone_number = validated_data.get("phone_number", instance.phone_number)

        location = validated_data.get("location", None)
        if location and (Location.objects.filter(region=location["region"]).exists()):
            instance.location = Location.objects.get(region=location["region"])

        full_name = validated_data.get("user", None)
        if full_name:
            serializer = FullNameSerializer(instance.user, data=full_name, partial=True)
            if serializer.is_valid():
                serializer.save()

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
