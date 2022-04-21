from django.conf import settings
from django.contrib import admin
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("courses.urls")),
    path("auth/", include("authentication.urls")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title='LizaAlert Volunteer Training Platform API',
            default_version='project',
            description=(
                'API description for LizaAlert volunteer training platform'
            ),
        ),
        public=True,
    )

    urlpatterns += [
        path(
            'swagger/',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'
        ),
        path(
            'redoc/',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc'
        ),
    ]

