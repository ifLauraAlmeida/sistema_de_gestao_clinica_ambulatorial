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

DEMO_PATIENTS: tuple[tuple[str, date], ...] = (
    ("Paciente Fictício Alfa", date(1985, 3, 12)),
    ("Paciente Fictício Bravo", date(1978, 7, 28)),
    ("Paciente Fictício Charlie", date(1992, 11, 15)),
    ("Paciente Fictício Delta", date(1980, 6, 3)),
    ("Paciente Fictício Echo", date(1988, 1, 22)),
    ("Paciente Fictício Foxtrot", date(1975, 9, 9)),
    ("Paciente Fictício Golf", date(1990, 4, 18)),
    ("Paciente Fictício Hotel", date(1982, 12, 30)),
)
