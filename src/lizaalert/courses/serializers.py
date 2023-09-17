from rest_framework import serializers

from lizaalert.courses.models import FAQ, Chapter, ChapterLesson, Course, CourseStatus, Knowledge, Lesson


class CourseCommonFieldsMixin(serializers.ModelSerializer):
    level = serializers.StringRelatedField(read_only=True)
    lessons_count = serializers.IntegerField()
    course_duration = serializers.IntegerField()
    course_status = serializers.StringRelatedField(read_only=True)


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
        )


class LessonInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка уроков курса."""

    lesson_type = serializers.ReadOnlyField(source="lesson.lesson_type")
    lesson_status = serializers.ReadOnlyField(source="lesson.lesson_status")
    duration = serializers.ReadOnlyField(source="lesson.duration")
    title = serializers.ReadOnlyField(source="lesson.title")

    class Meta:
        model = ChapterLesson
        fields = (
            "id",
            "order_number",
            "lesson_type",
            "lesson_status",
            "duration",
            "title",
        )


class ChapterInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка частей курса."""

    lessons = LessonInlineSerializer(source="chapterlesson_set", read_only=True, many=True)

    class Meta:
        model = Chapter
        fields = (
            "id",
            "title",
            "lessons",
        )


class FaqInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенных FAQ."""

    class Meta:
        model = FAQ
        fields = "__all__"


class KnowledgeInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенных умений."""

    class Meta:
        model = Knowledge
        fields = "__all__"


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(many=True)
    faq = FaqInlineSerializer(many=True)
    knowledge = KnowledgeInlineSerializer(many=True)

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
            "course_user_status",
        )


class CourseLessonListSerializer(serializers.ModelSerializer):
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
