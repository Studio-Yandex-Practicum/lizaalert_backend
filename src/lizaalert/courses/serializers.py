from rest_framework import serializers

from lizaalert.courses.models import FAQ, Chapter, Course, CourseStatus, Knowledge, Lesson


class FaqInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенных FAQ."""

    class Meta:
        model = FAQ
        fields = (
            "id",
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
            "id",
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
    """Course serializer."""

    user_course_progress = serializers.IntegerField(default=0)

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
            "user_course_progress",
        )


class LessonInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка уроков курса."""

    lesson_type = serializers.ReadOnlyField()
    duration = serializers.ReadOnlyField()
    title = serializers.ReadOnlyField()
    user_lesson_progress = serializers.IntegerField(default=0)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "order_number",
            "lesson_type",
            "duration",
            "title",
            "user_lesson_progress",
        )


class ChapterInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка частей курса."""

    lessons = LessonInlineSerializer(many=True)
    user_chapter_progress = serializers.IntegerField(default=0)

    class Meta:
        model = Chapter
        fields = (
            "id",
            "title",
            "user_chapter_progress",
            "lessons",
        )


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(many=True)
    user_status = serializers.StringRelatedField(default=False)
    user_course_progress = serializers.IntegerField(default=0)

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
            "user_course_progress",
        )


class LessonSerializer(serializers.ModelSerializer):
    next_lesson_id = serializers.IntegerField()
    prev_lesson_id = serializers.IntegerField()
    user_lesson_progress = serializers.IntegerField()
    course_id = serializers.IntegerField(source="chapter.course_id")

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course_id",
            "chapter_id",
            "title",
            "description",
            "lesson_type",
            "tags",
            "duration",
            "additional",
            "diploma",
            "user_lesson_progress",
            "next_lesson_id",
            "prev_lesson_id",
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
