from django.shortcuts import get_object_or_404
from rest_framework import serializers

from lizaalert.courses.models import FAQ, Chapter, Course, CourseStatus, Knowledge, Lesson, LessonProgressStatus


class FaqInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенных FAQ."""

    class Meta:
        model = FAQ
        fields = (
            "question",
            "answer",
            "author",
            "created_at",
            "updated_at",
        )


class KnowledgeInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенных умений."""

    class Meta:
        model = Knowledge
        fields = (
            "title",
            "description",
            "author",
            "created_at",
            "updated_at",
        )


class CourseCommonFieldsMixin(serializers.ModelSerializer):
    level = serializers.StringRelatedField(read_only=True)
    lessons_count = serializers.IntegerField()
    course_duration = serializers.IntegerField()
    course_status = serializers.StringRelatedField(read_only=True)
    user_status = serializers.StringRelatedField()
    faq = FaqInlineSerializer(many=True)
    knowledge = KnowledgeInlineSerializer(many=True)


class CourseStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseStatus
        fields = "__all__"


class CourseSerializer(CourseCommonFieldsMixin):
    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "level",
            "course_format",
            "short_description",
            "lessons_count",
            "course_duration",
            "course_status",
            "cover_path",
            "faq",
            "knowledge",
            "user_status",
        )


class LessonInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка уроков курса."""

    lesson_type = serializers.ReadOnlyField(source="lesson.lesson_type")
    lesson_progress = serializers.SerializerMethodField()
    duration = serializers.ReadOnlyField(source="lesson.duration")
    title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = Lesson
        fields = (
            "id",
            "order_number",
            "lesson_type",
            "lesson_progress",
            "duration",
            "title",
        )

    def get_lesson_progress(self, obj):
        try:
            user = self.context.get("request").user
            lesson = obj.lesson
            progress = get_object_or_404(LessonProgressStatus, user=user, lesson=lesson)
            return progress.userlessonprogress
        except Exception:
            return "0"


class ChapterInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка частей курса."""

    lessons = LessonInlineSerializer(many=True)

    class Meta:
        model = Chapter
        fields = (
            "id",
            "title",
            "lessons",
        )


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(many=True)
    user_status = serializers.StringRelatedField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "level",
            "full_description",
            "faq",
            "knowledge",
            "start_date",
            "cover_path",
            "lessons_count",
            "course_duration",
            "chapters",
            "user_status",
        )


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "description",
            "lesson_type",
            "tags",
            "duration",
            "additional",
            "diploma",
        )


class OptionSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField()


class FilterSerializer(serializers.Serializer):
    slug = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    def get_name(self, model):
        return model._meta.verbose_name

    def get_slug(self, model):
        return model._meta.model_name

    def get_options(self, model):
        return OptionSerializer(model.objects.all(), many=True).data
