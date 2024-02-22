from django.urls import path

from lizaalert.webinars.views import WebinarViewSet

urlpatterns = [
    path(
        "lessons/<int:lesson_id>/homework/",
        WebinarViewSet.as_view({"get": "retrieve"}),
        name="lesson-homework-detail",
    ),
]
