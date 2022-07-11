from rest_framework import serializers
from .models import Level


class LevelSerializer(serializers.ModelSerializer):
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Level
        exclude = ('description', )

    def get_slug(self, obj):
        return obj.get_name_display()
