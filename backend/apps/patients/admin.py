from django.contrib import admin

from apps.patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Consulta administrativa de cadastros."""

    list_display = ("full_name", "birth_date", "is_active")
    search_fields = ("full_name", "social_name")
    list_filter = ("is_active",)
