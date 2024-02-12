from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from lizaalert.homeworks.models import Homework
from lizaalert.courses.models import Subscription, Lesson


class HomeworkSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для домашних работ."""
    status = serializers.ChoiceField(choices=Homework.ProgressionStatus)
    reviewer = serializers.StringRelatedField(read_only=True)
    subscription = serializers.PrimaryKeyRelatedField(queryset=Subscription.objects.all())
#    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    class Meta:
        model = Homework
        fields = (
            "id",
            "reviewer",
            "status",
            "lesson",
            "text",
            "subscription",
            "required",
        )

#     def create(self, validated_data):
#         if 'id' not in self.initial_data:
# #            homework = Homework.objects.create(**validated_data)
            
#             return HomeworkSerializer(validated_data)
#         else:
#             print(1111)
#             print('id' in self.initial_data)
#             print(self.initial_data)
#             print(validated_data)
#             homework = Homework.objects.get(id=self.initial_data.get('id'))
#             homework.text = self.initial_data.get('text')
#             homework.status = Homework.ProgressionStatus.SUBMITTED
#             homework.save
#             return homework


class HomeworkDetailSerializer(HomeworkSerializer):
    """Сериалайзер класс для домашней работы."""

    pass
