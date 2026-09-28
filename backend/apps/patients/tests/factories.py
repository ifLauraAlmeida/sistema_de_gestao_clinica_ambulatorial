from datetime import date

from apps.patients.cpf import is_valid_cpf
from apps.patients.models import Patient


def build_fake_cpf(base_digits: str) -> str:
    """Gera CPF fictício válido a partir de 9 dígitos, calculando os verificadores."""
    for suffix in range(100):
        candidate = f"{base_digits}{suffix:02d}"
        if is_valid_cpf(candidate):
            return candidate
    raise ValueError(f"base inválida para CPF: recebido='{base_digits}', esperado 9 dígitos")


def create_patient(full_name: str = "Paciente Fictício", **fields: object) -> Patient:
    fields.setdefault("birth_date", date(1990, 1, 1))
    return Patient.objects.create(full_name=full_name, **fields)
