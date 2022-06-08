from django.urls import path

from .views import VolunteerAPIview


urlpatterns = [
    path("profile/<int:volunteer_id>/",
         VolunteerAPIview.as_view(),
         name="profile"),
]
