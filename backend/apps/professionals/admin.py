from django.contrib import admin

from apps.professionals.models import Professional, Specialty


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    """Cadastro de especialidades e prefixos de senha."""

    list_display = ("name", "ticket_prefix", "is_active")
    list_filter = ("is_active",)


@admin.register(Professional)
class ProfessionalAdmin(admin.ModelAdmin):
    """Cadastro de profissionais e suas especialidades."""

    list_display = ("user", "council_registration", "is_active")
    filter_horizontal = ("specialties",)
    list_select_related = ("user",)
