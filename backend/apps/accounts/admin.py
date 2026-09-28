from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Administração de usuários com o campo de perfil."""

    list_display = ("username", "first_name", "last_name", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = (
        *DjangoUserAdmin.fieldsets,  # type: ignore[misc]
        ("Perfil de acesso", {"fields": ("role",)}),
    )
    add_fieldsets = (
        *DjangoUserAdmin.add_fieldsets,
        ("Perfil de acesso", {"fields": ("role",)}),
    )
