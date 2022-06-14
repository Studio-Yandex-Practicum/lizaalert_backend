from django.urls import path

from .views import VolunteerAPIview


urlpatterns = [
    path("profile/", VolunteerAPIview.as_view(), name="profile"),
]
