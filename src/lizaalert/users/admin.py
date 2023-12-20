from django import forms
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


class BadgeAdminForm(forms.ModelForm):
    class Meta:
        model = Badge
        fields = "__all__"

    def clean(self):
        """
        Переопределение метода clean для выполнения пользовательской валидации полей формы.

        Выполняет проверку, что поля `threshold_courses` и `threshold_course` не заполнены одновременно.
        В случае обнаружения одновременного заполнения, добавляет сообщение об ошибке к соответствующим полям.
        """
        cleaned_data = super().clean()
        threshold_courses = cleaned_data.get("threshold_courses")
        threshold_course = cleaned_data.get("threshold_course")

        if threshold_courses and threshold_course:
            self.add_error(
                "threshold_courses", "Эти поля не могут быть записаны одновременно, нужно выбрать только одно."
            )
            self.add_error(
                "threshold_course", "Эти поля не могут быть записаны одновременно, нужно выбрать только одно."
            )


class BadgeAdmin(admin.ModelAdmin):
    form = BadgeAdminForm
    inlines = [VolunteerBadgeInline]


class VolunteerBadgeAdminForm(forms.ModelForm):
    class Meta:
        model = VolunteerBadge
        fields = "__all__"

    def clean(self):
        """Проверка на уникальность значков для волонтеров."""
        cleaned_data = super().clean()
        volunteer = cleaned_data.get("volunteer")
        badge = cleaned_data.get("badge")

        if volunteer and badge:
            if VolunteerBadge.objects.filter(volunteer=volunteer, badge=badge).exclude(id=self.instance.id).exists():
                self.add_error(None, "Этот значок уже был выдан данному волонтеру.")


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
