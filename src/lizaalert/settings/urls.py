from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from lizaalert.authentication.views import LoginView

admin.site.site_header = "ЛизаАлерт"
admin.site.site_title = "ЛизаАлерт"

urlpatterns = []

if settings.YANDEX_AUTH:
    urlpatterns += [
        path("admin/login/", LoginView.as_view(), name="login"),
    ]

urlpatterns += [
    path("admin/", admin.site.urls),
    path("api/v1/", include("lizaalert.courses.urls")),
    path("api/v1/", include("lizaalert.quizzes.urls")),
    path("api/v1/", include("lizaalert.webinars.urls")),
    path("api/v1/", include("lizaalert.users.urls")),
    path("api/v1/", include("lizaalert.authentication.urls")),
    path("api/v1/auth/", include("djoser.urls.jwt")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="LizaAlert Volunteer Training Platform API",
            default_version="project",
            description=("API description for LizaAlert volunteer training platform"),
        ),
        url=settings.API_URL,
        public=True,
    )

    urlpatterns += [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    ]
# if settings.YANDEX_AUTH:
#     urlpatterns.insert(0, path("admin/login/", LoginView.as_view(), name="login"))
