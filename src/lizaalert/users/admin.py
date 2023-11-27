from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from lizaalert.users.models import (
    Badge,
    Department,
    Level,
    Location,
    User,
    UserRole,
    Volunteer,
    VolunteerBadge,
    VolunteerCourse,
    VolunteerLevel,
)


class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (("Контактная информация", {"fields": ("phone",)}),)


class VolunteerLevelInline(admin.TabularInline):
    model = VolunteerLevel
    extra = 1


class VolunteerBadgeInline(admin.TabularInline):
    model = VolunteerBadge
    extra = 1


class LevelAdmin(admin.ModelAdmin):
    inlines = [VolunteerLevelInline]


class BadgeAdmin(admin.ModelAdmin):
    inlines = [VolunteerBadgeInline]


class VolunteerAdmin(admin.ModelAdmin):
    inlines = [VolunteerLevelInline, VolunteerBadgeInline]


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserRole)
admin.site.register(Volunteer, VolunteerAdmin)
admin.site.register(VolunteerCourse)
admin.site.register(Location)
admin.site.register(Department)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(Level, LevelAdmin)
