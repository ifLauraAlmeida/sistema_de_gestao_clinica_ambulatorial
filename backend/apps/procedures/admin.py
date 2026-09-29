from django.contrib import admin
from django.http import HttpRequest

from apps.procedures.models import ProcedureRecord


@admin.register(ProcedureRecord)
class ProcedureRecordAdmin(admin.ModelAdmin):
    """Consulta somente leitura das versões registradas."""

    list_display = ("encounter", "template", "recorded_by", "recorded_at")
    list_select_related = ("encounter", "template", "recorded_by")

    def has_change_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False

    def has_delete_permission(self, request: HttpRequest, obj: object = None) -> bool:
        return False
