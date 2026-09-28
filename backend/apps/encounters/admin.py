from django.contrib import admin

from apps.encounters.models import Encounter, EncounterStatusChange


class EncounterStatusChangeInline(admin.TabularInline):
    model = EncounterStatusChange
    extra = 0
    can_delete = False
    readonly_fields = ("previous_status", "new_status", "changed_by", "changed_at")


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    """Consulta administrativa de atendimentos (histórico não editável)."""

    list_display = ("ticket_code", "service_date", "patient", "professional", "status")
    list_filter = ("status", "specialty", "service_date")
    list_select_related = ("patient", "professional__user")
    readonly_fields = (
        "patient",
        "appointment",
        "professional",
        "specialty",
        "ticket_code",
        "service_date",
        "status",
        "checked_in_at",
        "completed_at",
        "created_by",
    )
    inlines = (EncounterStatusChangeInline,)
