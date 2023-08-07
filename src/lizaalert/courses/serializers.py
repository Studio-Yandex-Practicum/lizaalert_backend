from rest_framework import serializers

from lizaalert.courses.models import Chapter, ChapterLesson, Course, CourseStatus, Lesson

from lizaalert.users.models import Level

from lizaalert.users.serializers import LevelSerializer


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


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(many=True)
    knowledge = serializers.JSONField()

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


class FilterSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    options = serializers.SerializerMethodField()

    def get_options(self, obj):
        if obj["slug"] == "level":
            levels = Level.objects.all()
            serializer = LevelSerializer(levels, many=True)
        elif obj["slug"] == "course_status":
            statuses = CourseStatus.objects.all()
            serializer = CourseStatusSerializer(statuses, many=True)
        else:
            return []

        return serializer.data
