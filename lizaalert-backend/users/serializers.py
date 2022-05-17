from rest_framework import serializers

from .models import CourseStatus


class CourseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatus
        fields = "__all__"
