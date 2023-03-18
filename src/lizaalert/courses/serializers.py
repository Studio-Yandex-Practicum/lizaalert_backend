from rest_framework import serializers

from lizaalert.courses.models import Chapter, ChapterLesson, Course, CourseStatus, Lesson


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
            "short_description",
            "lessons_count",
            "course_duration",
            "course_status",
            "cover_path",
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
            "knowledge",
            "start_date",
            "cover_path",
            "lessons_count",
            "course_duration",
            "chapters",
            "knowledge",
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
