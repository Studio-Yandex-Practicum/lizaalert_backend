from django.urls import path

from .views import VolunteerAPIview


urlpatterns = [
    path("profile/<int:user_id>/",
         VolunteerAPIview.as_view(),
         name="profile"),
]
