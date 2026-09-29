from django.contrib import admin

from apps.catalog.models import (
    ExecutionFormField,
    ExecutionFormTemplate,
    LaboratoryExam,
    Service,
    ServiceAlias,
    ServiceCategory,
    ServiceGroup,
    ServicePackage,
    ServicePackageItem,
)


class ServiceGroupInline(admin.TabularInline):
    model = ServiceGroup
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "is_active")
    inlines = (ServiceGroupInline,)


class ServiceAliasInline(admin.TabularInline):
    model = ServiceAlias
    extra = 0


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Cadastro de serviços pelo gestor: tempos, preços, preparo e atributos."""

    list_display = (
        "name",
        "service_type",
        "group",
        "specialty",
        "duration_minutes",
        "reference_price",
        "is_active",
    )
    list_filter = ("service_type", "group__category", "specialty", "is_active")
    search_fields = ("name", "aliases__name")
    list_select_related = ("group__category", "specialty")
    inlines = (ServiceAliasInline,)


class ExecutionFormFieldInline(admin.TabularInline):
    model = ExecutionFormField
    extra = 0


@admin.register(ExecutionFormTemplate)
class ExecutionFormTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    inlines = (ExecutionFormFieldInline,)


@admin.register(LaboratoryExam)
class LaboratoryExamAdmin(admin.ModelAdmin):
    list_display = ("name", "group", "sample_type", "fasting_hours", "is_active")
    list_filter = ("group", "sample_type", "is_active")
    search_fields = ("name",)


class ServicePackageItemInline(admin.TabularInline):
    model = ServicePackageItem
    extra = 0
    autocomplete_fields = ("service", "laboratory_exam")


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    inlines = (ServicePackageItemInline,)
