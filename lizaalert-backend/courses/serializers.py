from rest_framework import serializers

from .models import Course, CourseStatus


class CourseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatus
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    level = serializers.StringRelatedField(read_only=True)
    lessons_count = serializers.IntegerField()
    course_duration = serializers.IntegerField()
    course_status = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = (
            "title",
            "level",
            "short_description",
            "lessons_count",
            "course_duration",
            "course_status",
            "cover_path",
        )
