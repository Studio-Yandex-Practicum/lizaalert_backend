from django.urls import include, path
from rest_framework import routers

from lizaalert.homeworks.views import HomeworkViewSet

router = routers.SimpleRouter()
router.register(r"lessons/(?P<lesson_id>\d+)/homeworks", HomeworkViewSet, basename="homework")


urlpatterns = [
    path("", include(router.urls)),
]
