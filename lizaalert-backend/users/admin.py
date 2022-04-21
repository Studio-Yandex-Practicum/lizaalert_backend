from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Badge, Level, User, Volunteer


class CustomUserAdmin(UserAdmin):
    class Meta:
        model = User


admin.site.register(Badge)
admin.site.register(Level)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Volunteer)
