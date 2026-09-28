"""
Registros fictícios de demonstração.

Nomes inventados, sem CPF e sem dados clínicos: nunca utilizar dados reais.
"""

from datetime import date

from apps.accounts.models import UserRole

DEMO_USERS: tuple[tuple[str, str, str, UserRole], ...] = (
    ("recepcao.demo", "Ana", "Recepção", UserRole.ATENDENTE),
    ("medica.demo", "Beatriz", "Gineco", UserRole.MEDICO),
    ("medico.demo", "Carlos", "Orto", UserRole.MEDICO),
    ("gestao.demo", "Diana", "Gestão", UserRole.GESTOR),
)

# username do médico -> (nome da especialidade, prefixo da senha)
DEMO_DOCTOR_SPECIALTIES: dict[str, tuple[str, str]] = {
    "medica.demo": ("Ginecologia", "GINE"),
    "medico.demo": ("Ortopedia", "ORTO"),
}

DEMO_RECEPTION_DESKS = ("Guichê 01", "Guichê 02", "Guichê 03")
DEMO_CONSULTATION_ROOMS = ("Consultório 01", "Consultório 02", "Consultório 03", "Consultório 04")

# Telefones com DDD 00, inexistente, para nunca coincidirem com números reais.
DEMO_PATIENTS: tuple[tuple[str, date, str], ...] = (
    ("Paciente Fictício Alfa", date(1985, 3, 12), "(00) 90000-0001"),
    ("Paciente Fictício Bravo", date(1978, 7, 28), "(00) 90000-0002"),
    ("Paciente Fictício Charlie", date(1992, 11, 15), "(00) 90000-0003"),
    ("Paciente Fictício Delta", date(1980, 6, 3), "(00) 90000-0004"),
    ("Paciente Fictício Echo", date(1988, 1, 22), "(00) 90000-0005"),
    ("Paciente Fictício Foxtrot", date(1975, 9, 9), "(00) 90000-0006"),
    ("Paciente Fictício Golf", date(1990, 4, 18), "(00) 90000-0007"),
    ("Paciente Fictício Hotel", date(1982, 12, 30), "(00) 90000-0008"),
)
