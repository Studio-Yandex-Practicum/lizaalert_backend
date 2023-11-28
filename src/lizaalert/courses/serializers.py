from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from lizaalert.courses.models import FAQ, Chapter, Course, Knowledge, Lesson
from lizaalert.courses.utils import BreadcrumbSchema, CurrentLessonSerializer, NeighbourLessonSerializer


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
            "order_number",
            "lessons",
        )


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(many=True)
    user_status = serializers.StringRelatedField(default=False)
    user_course_progress = serializers.IntegerField(default=0)
    current_lesson = serializers.SerializerMethodField()

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
            "current_lesson",
        )

    @swagger_serializer_method(serializer_or_field=CurrentLessonSerializer)
    def get_current_lesson(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            current_lesson = CurrentLessonSerializer({"chapter": obj.current_chapter, "lesson": obj.current_lesson})
            return current_lesson.data
        return None


class LessonSerializer(serializers.ModelSerializer):
    next_lesson = serializers.SerializerMethodField()
    prev_lesson = serializers.SerializerMethodField()
    user_lesson_progress = serializers.IntegerField(default=0)
    course_id = serializers.IntegerField(source="chapter.course_id")
    breadcrumbs = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "course_id",
            "chapter_id",
            "title",
            "description",
            "video_link",
            "lesson_type",
            "tags",
            "duration",
            "additional",
            "diploma",
            "breadcrumbs",
            "user_lesson_progress",
            "next_lesson",
            "prev_lesson",
        )

    @swagger_serializer_method(serializer_or_field=BreadcrumbSchema)
    def get_breadcrumbs(self, obj):
        breadcrumb_serializer = BreadcrumbSchema({"course": obj.chapter.course, "chapter": obj.chapter})
        return breadcrumb_serializer.data

    @swagger_serializer_method(serializer_or_field=NeighbourLessonSerializer)
    def get_next_lesson(self, obj):
        current_lesson = NeighbourLessonSerializer({"chapter_id": obj.next_chapter_id, "lesson_id": obj.next_lesson_id})
        return current_lesson.data

    @swagger_serializer_method(serializer_or_field=NeighbourLessonSerializer)
    def get_prev_lesson(self, obj):
        current_lesson = NeighbourLessonSerializer({"chapter_id": obj.prev_chapter_id, "lesson_id": obj.prev_lesson_id})
        return current_lesson.data


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
