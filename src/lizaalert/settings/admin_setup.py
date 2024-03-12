from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected as delete_selected_original
from django.utils.translation import ngettext


class ShowDeletedObjectsFilter(admin.SimpleListFilter):
    """
    Фильтр для django admin.

    Позволяет показывать/скрывать удаленные записи в админке.
    """

    title = "Показать удаленные записи"
    parameter_name = "is_deleted"

    def lookups(self, request, model_admin):
        return (
            ("1", ("Показать удаленные")),
            ("0", ("Скрыть удаленные")),
        )

    def queryset(self, request, queryset):
        match self.value():
            case "1":
                return queryset.filter(deleted_at__isnull=False)
            case "0":
                return queryset.filter(deleted_at__isnull=True)
        return queryset


class BaseAdmin(admin.ModelAdmin):
    """
    База для панели админа.

    По дефолту добавляет фильтр удаленных объектов, флаг удаленности и запрещает редактировать
     дату удаления.
    Добавляет действия восстановления и мягкого удаления выбранных объектов.
    Использует менеджер модели с отображением всех объектов в базе данных.
    Стандарнтый текст для удаления объектов заменен на новый, сообщающий о безвозвратном удалении.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display += ("is_deleted",)
        self.readonly_fields += ("deleted_at",)
        self.actions = ("soft_restore", "soft_delete_selected", "delete_selected_custom")
        self.list_filter += (ShowDeletedObjectsFilter,)

    def get_queryset(self, request):
        """Возвращает queryset, исключая удаленные записи."""
        return self.model.all_objects.all()

    @admin.action(description="Удалить выбранные объекты")
    def soft_delete_selected(self, request, queryset):
        qs = self.model.objects.filter(pk__in=queryset.values_list("pk", flat=True))
        qs.delete()

    @admin.display(description="Доступен")
    def is_deleted(self, obj):
        """Флаг удаленности."""
        return bool(not obj.deleted_at)

    is_deleted.boolean = True

    @admin.action(description="Восстановить выбранные объекты")
    def soft_restore(self, request, queryset):
        """Восстановление удаленных объектов."""
        updated = queryset.update(deleted_at=None)
        self.message_user(
            request,
            ngettext(
                "%d запись была успешно восстановлена.",
                "%d записей было успешко восстановлено.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description="Безвозвратно удалить выбранные объекты")
    def delete_selected_custom(self, request, queryset):
        return delete_selected_original(self, request, queryset)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if "delete_selected" in actions:
            del actions["delete_selected"]
        return actions
