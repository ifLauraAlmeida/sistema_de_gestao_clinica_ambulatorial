"""
Registros fictícios de demonstração.

Nomes inventados, sem CPF e sem dados clínicos: nunca utilizar dados reais.
"""

from dataclasses import dataclass
from datetime import date

from apps.accounts.models import UserRole
from apps.workstations.models import StationType


@dataclass(frozen=True)
class DemoUser:
    username: str
    first_name: str
    last_name: str
    role: UserRole
    # Prefixos de senha das especialidades atendidas (vazio para quem não atende).
    specialty_prefixes: tuple[str, ...] = ()


DEMO_USERS: tuple[DemoUser, ...] = (
    DemoUser("recepcao.demo", "Ana", "Recepção", UserRole.ATENDENTE),
    DemoUser("recepcao2.demo", "Bia", "Recepção", UserRole.ATENDENTE),
    DemoUser("medica.demo", "Beatriz", "Pediatra", UserRole.MEDICO, ("PEDI", "USG", "DOP")),
    DemoUser("medico.demo", "Carlos", "Orto", UserRole.MEDICO, ("ORTO",)),
    DemoUser("nutri.demo", "Nina", "Nutricionista", UserRole.PROFISSIONAL_SAUDE, ("NUTR",)),
    DemoUser("dentista.demo", "Davi", "Dentista", UserRole.PROFISSIONAL_SAUDE, ("ODON",)),
    DemoUser("psico.demo", "Paula", "Psicóloga", UserRole.PROFISSIONAL_SAUDE, ("PSIC",)),
    DemoUser("fono.demo", "Flora", "Fonoaudióloga", UserRole.PROFISSIONAL_SAUDE, ("AUDIO",)),
    DemoUser("tecnico.rx", "Rafael", "Radiologia", UserRole.TECNICO, ("RX", "MAMO", "DENS")),
    DemoUser("tecnico.lab", "Luana", "Coleta", UserRole.TECNICO, ("LAB",)),
    DemoUser("gestao.demo", "Diana", "Gestão", UserRole.GESTOR),
)

DEMO_STATIONS: tuple[tuple[StationType, str], ...] = (
    *((StationType.RECEPTION_DESK, f"Guichê 0{number}") for number in range(1, 4)),
    *((StationType.CONSULTATION_ROOM, f"Consultório 0{number}") for number in range(1, 5)),
    (StationType.EXAM_ROOM, "Sala de Raio-X"),
    (StationType.EXAM_ROOM, "Sala de Mamografia e Densitometria"),
    (StationType.EXAM_ROOM, "Sala de Ultrassom"),
    (StationType.EXAM_ROOM, "Sala de Coleta"),
    (StationType.EXAM_ROOM, "Cabine de Audiometria"),
)

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


@dataclass(frozen=True)
class DemoAppointment:
    professional_username: str
    service_name: str
    laterality: str = ""
    laboratory_exams: tuple[str, ...] = ()


# Agenda do dia, na ordem dos pacientes acima.
DEMO_TODAY_AGENDA: tuple[DemoAppointment, ...] = (
    DemoAppointment("medica.demo", "Consulta pediátrica — primeira consulta"),
    DemoAppointment("medico.demo", "Consulta ortopédica — primeira consulta"),
    DemoAppointment("tecnico.rx", "Raio-X de joelho", laterality="DIREITA"),
    DemoAppointment(
        "tecnico.lab",
        "Coleta de exames laboratoriais",
        laboratory_exams=("Hemograma completo", "Glicemia de jejum", "TSH"),
    ),
    DemoAppointment("nutri.demo", "Bioimpedância"),
    DemoAppointment("medica.demo", "Ultrassonografia de abdome total"),
    DemoAppointment("tecnico.rx", "Mamografia bilateral"),
    DemoAppointment("psico.demo", "Sessão de psicologia individual"),
)
