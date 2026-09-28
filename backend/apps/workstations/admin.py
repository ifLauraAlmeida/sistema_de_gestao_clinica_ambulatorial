from django.contrib import admin

from apps.workstations.models import Station, WorkSession


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    """Cadastro de guichês e consultórios pelo gestor."""

    list_display = ("name", "station_type", "is_active")
    list_filter = ("station_type", "is_active")
    search_fields = ("name",)


@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    """Consulta das sessões de trabalho (histórico não editável)."""

    list_display = ("user", "station", "started_at", "ended_at")
    list_filter = ("station_type",)
    readonly_fields = ("user", "station", "station_type", "started_at", "ended_at")
