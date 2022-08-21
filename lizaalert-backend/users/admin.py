from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Badge, Level, Location, User, UserRole, Volunteer, VolunteerCourse


class CustomUserAdmin(UserAdmin):
    class Meta:
        model = User


admin.site.register(Badge)
admin.site.register(Level)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserRole)
admin.site.register(Volunteer)
admin.site.register(VolunteerCourse)
admin.site.register(Location)
