from rest_framework import serializers

from .models import Course, CourseStatus


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CourseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatus
        fields = "__all__"
