from django.urls import path

from lizaalert.webinars.views import WebinarViewSet

urlpatterns = [
    path(
        "lessons/<int:lesson_id>/webinar/",
        WebinarViewSet.as_view({"get": "retrieve"}),
        name="lesson-webinar-detail",
    ),
]
