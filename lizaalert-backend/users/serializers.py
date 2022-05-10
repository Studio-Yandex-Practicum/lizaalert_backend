from rest_framework import serializers

from .models import Badge, Volunteer, VolunteerCourse


class BageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ["name", "description", ]


class VolunteerSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    badges = BageSerializer(many=True)
    count_pass_course = serializers.SerializerMethodField()

    class Meta:
        model = Volunteer
        fields = ["id", "phone_number", "email", "full_name",
                  "birth_date", "location", "photo", "level", "badges",
                  "count_pass_course"
                  ]

    def get_location(self, obj):
        location = obj.location
        if location:
            return location.region
        return None

    def get_email(self, obj):
        user = obj.user
        return user.email

    def get_full_name(self, obj):
        user = obj.user
        return user.first_name + ' ' + user.last_name

    def get_photo(self, obj):
        request = self.context.get("request")
        if obj.photo:
            photo_url = obj.photo.url
            return request.build_absolute_uri(photo_url)
        return None

    def get_level(self, obj):
        level = obj.level
        return level.name

    def get_count_pass_course(self, obj):
        courses = VolunteerCourse.objects.filter(volunteer=obj.pk,
                                                 status="Пройден")
        return len(courses)
