from apps.accounts.models import User
from apps.professionals.models import Professional, Specialty


def create_specialty(name: str = "Ginecologia", ticket_prefix: str = "GINE") -> Specialty:
    return Specialty.objects.create(name=name, ticket_prefix=ticket_prefix)


def create_professional(user: User, *specialties: Specialty) -> Professional:
    professional = Professional.objects.create(user=user)
    professional.specialties.set(specialties)
    return professional
