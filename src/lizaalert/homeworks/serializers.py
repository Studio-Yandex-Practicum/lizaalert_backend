from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject

from lizaalert.homeworks.models import Homework, ProgressionStatus


class HomeworkSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для домашних работ."""

    status = serializers.ChoiceField(choices=ProgressionStatus.choices)
    reviewer = serializers.StringRelatedField(read_only=True)
    subscription = serializers.PrimaryKeyRelatedField(read_only=True)
    lesson = serializers.PrimaryKeyRelatedField(read_only=True)
    required = serializers.BooleanField(read_only=True)

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

    def to_representation(self, instance):
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            if field.field_name == "status":
                ret[field.field_name] = ProgressionStatus.__dict__["_value2label_map_"].get(attribute)
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class EmptyHomeworkSerializer(serializers.Serializer):
    """Сериалайзер класс для домашних работ."""

    status = serializers.CharField(initial=ProgressionStatus.DRAFT.label)
    text = serializers.CharField(default="", initial="")
