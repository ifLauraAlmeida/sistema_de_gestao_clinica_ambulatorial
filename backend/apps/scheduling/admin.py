from django.contrib import admin

from apps.scheduling.models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Consulta administrativa da agenda."""

    list_display = ("scheduled_for", "patient", "professional", "specialty", "status")
    list_filter = ("status", "specialty")
    list_select_related = ("patient", "professional__user", "specialty")
    date_hierarchy = "scheduled_for"
