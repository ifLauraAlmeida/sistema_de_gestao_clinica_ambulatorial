from django.contrib import admin

from apps.billing.models import EncounterBilling, HealthInsurer


@admin.register(HealthInsurer)
class HealthInsurerAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)


@admin.register(EncounterBilling)
class EncounterBillingAdmin(admin.ModelAdmin):
    list_display = ("encounter", "payer_type", "insurer", "status", "amount", "updated_by")
    list_filter = ("status", "payer_type", "insurer")
    list_select_related = ("encounter", "insurer", "updated_by")
