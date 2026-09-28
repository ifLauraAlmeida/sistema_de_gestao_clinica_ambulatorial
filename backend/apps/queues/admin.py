from django.contrib import admin

from apps.queues.models import QueueCall, QueueEntry


@admin.register(QueueEntry)
class QueueEntryAdmin(admin.ModelAdmin):
    """Consulta das filas (somente leitura: alterações passam pelos serviços)."""

    list_display = ("encounter", "queue_type", "professional", "status", "entered_at")
    list_filter = ("queue_type", "status")
    list_select_related = ("encounter", "professional__user")

    def has_change_permission(self, request: object, obj: object = None) -> bool:
        return False


@admin.register(QueueCall)
class QueueCallAdmin(admin.ModelAdmin):
    """Histórico de chamadas (somente leitura)."""

    list_display = ("queue_entry", "destination_label", "attempt_number", "called_by", "called_at")
    list_select_related = ("queue_entry__encounter", "called_by")

    def has_change_permission(self, request: object, obj: object = None) -> bool:
        return False
