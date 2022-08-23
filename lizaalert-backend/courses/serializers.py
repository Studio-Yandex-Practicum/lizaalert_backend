from rest_framework import serializers

from .models import Course, CourseStatus, Chapter, Lesson


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
        fields = ('id', 'title', 'level', 'short_description', 'lessons_count', 'course_duration',
                  'course_status', 'cover_path'
                  )


class LessonInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка уроков курса"""

    class Meta:
        model = Lesson
        fields = ('lesson_type', 'lesson_status',)


class ChapterInlineSerializer(serializers.ModelSerializer):
    """Сериалайзер класс для вложенного списка частей курса"""
    lessons = LessonInlineSerializer(read_only=True, many=True)

    class Meta:
        model = Chapter
        fields = ('title', 'lessons')


class CourseDetailSerializer(CourseCommonFieldsMixin):
    chapters = ChapterInlineSerializer(read_only=True, many=True)

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'level', 'full_description', 'start_date', 'cover_path', 'lessons_count',
            'course_duration', 'chapters',
        )
