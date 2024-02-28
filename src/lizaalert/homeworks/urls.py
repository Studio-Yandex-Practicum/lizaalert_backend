from django.urls import path

from lizaalert.homeworks.views import HomeworkViewSet

urlpatterns = [
    path(
        "lessons/<int:lesson_id>/homework/",
        HomeworkViewSet.as_view({"get": "retrieve", "post": "create"}),
        name="lesson-homework-detail",
    ),
]
