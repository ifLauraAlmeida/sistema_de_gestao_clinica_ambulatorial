"""
Parâmetros do histórico fictício de demonstração.

Nomes montados a partir de listas genéricas, sem CPF e com telefone de DDD 00.
Textos clínicos são genéricos e fictícios.
"""

from dataclasses import dataclass

FIRST_NAMES = (
    "Adriana",
    "Bruno",
    "Camila",
    "Daniel",
    "Eduarda",
    "Felipe",
    "Gabriela",
    "Henrique",
    "Isabela",
    "João",
    "Karina",
    "Lucas",
    "Mariana",
    "Nicolas",
    "Olívia",
    "Pedro",
    "Rafaela",
    "Samuel",
    "Tatiana",
    "Vinícius",
    "Yasmin",
    "Leonardo",
    "Beatriz",
    "Caio",
)
LAST_NAMES = (
    "Almeida",
    "Barbosa",
    "Cardoso",
    "Duarte",
    "Esteves",
    "Freitas",
    "Gomes",
    "Henriques",
    "Lacerda",
    "Monteiro",
    "Nogueira",
    "Oliveira",
    "Pacheco",
    "Queiroz",
    "Rezende",
    "Siqueira",
)
HISTORY_PATIENT_COUNT = 90

# Recepcionistas e guichês usados no histórico.
RECEPTIONISTS = (("recepcao.demo", "Guichê 01"), ("recepcao2.demo", "Guichê 02"))

GESTOR_USERNAME = "gestao.demo"


@dataclass(frozen=True)
class ProfessionalPlan:
    """Agenda diária típica de um profissional e onde ele atende."""

    username: str
    station_name: str
    daily_appointments: int
    # (nome do serviço, peso no sorteio)
    services: tuple[tuple[str, int], ...]
    writes_clinical_notes: bool


PROFESSIONAL_PLANS: tuple[ProfessionalPlan, ...] = (
    ProfessionalPlan(
        "medica.demo",
        "Consultório 01",
        5,
        (
            ("Consulta pediátrica — primeira consulta", 3),
            ("Consulta pediátrica — retorno", 3),
            ("Consulta pediátrica de acompanhamento", 2),
            ("Ultrassonografia de abdome total", 2),
            ("Ultrassonografia de tireoide", 1),
            ("Doppler venoso de membros inferiores", 1),
        ),
        True,
    ),
    ProfessionalPlan(
        "medico.demo",
        "Consultório 02",
        4,
        (
            ("Consulta ortopédica — primeira consulta", 3),
            ("Consulta ortopédica — retorno", 3),
            ("Avaliação ortopédica", 1),
            ("Imobilização ortopédica", 1),
        ),
        True,
    ),
    ProfessionalPlan(
        "nutri.demo",
        "Consultório 03",
        3,
        (
            ("Consulta de Nutrição — primeira consulta", 2),
            ("Consulta de Nutrição — retorno", 2),
            ("Bioimpedância", 2),
        ),
        True,
    ),
    ProfessionalPlan(
        "dentista.demo",
        "Consultório 04",
        3,
        (
            ("Consulta odontológica — avaliação", 2),
            ("Profilaxia / limpeza dentária", 2),
            ("Restauração dentária", 1),
        ),
        True,
    ),
    ProfessionalPlan(
        "psico.demo",
        "Consultório 03",
        2,
        (("Sessão de psicologia individual", 3), ("Avaliação psicológica inicial", 1)),
        True,
    ),
    ProfessionalPlan(
        "fono.demo",
        "Consultório 04",
        2,
        (("Audiometria tonal limiar", 2), ("Imitanciometria completa", 1)),
        True,
    ),
    ProfessionalPlan(
        "tecnico.rx",
        "Sala de Raio-X",
        6,
        (
            ("Raio-X de tórax PA", 3),
            ("Raio-X de joelho", 2),
            ("Raio-X de coluna lombar", 2),
            ("Mamografia bilateral", 2),
            ("Densitometria óssea — coluna + fêmur", 1),
        ),
        False,
    ),
    ProfessionalPlan(
        "tecnico.lab",
        "Sala de Coleta",
        5,
        (("Coleta de exames laboratoriais", 1),),
        False,
    ),
)

# Preços fictícios de referência (aplicados só se ainda não definidos).
HISTORY_REFERENCE_PRICES: dict[str, str] = {
    "Consulta pediátrica — retorno": "180.00",
    "Consulta pediátrica de acompanhamento": "220.00",
    "Ultrassonografia de tireoide": "230.00",
    "Doppler venoso de membros inferiores": "420.00",
    "Consulta ortopédica — retorno": "220.00",
    "Avaliação ortopédica": "250.00",
    "Imobilização ortopédica": "180.00",
    "Consulta de Nutrição — primeira consulta": "240.00",
    "Consulta de Nutrição — retorno": "160.00",
    "Consulta odontológica — avaliação": "150.00",
    "Profilaxia / limpeza dentária": "180.00",
    "Restauração dentária": "260.00",
    "Avaliação psicológica inicial": "250.00",
    "Audiometria tonal limiar": "130.00",
    "Imitanciometria completa": "120.00",
    "Raio-X de tórax PA": "90.00",
    "Raio-X de coluna lombar": "130.00",
    "Densitometria óssea — coluna + fêmur": "240.00",
}

# Probabilidades de desfecho de um agendamento passado.
CANCELLED_RATE = 0.05
NO_SHOW_BEFORE_ARRIVAL_RATE = 0.07
NO_SHOW_AFTER_CALL_RATE = 0.02
PENDING_PAYMENT_RATE = 0.03
INSURANCE_RATE = 0.35

CLINICAL_NOTES = (
    "Paciente refere melhora dos sintomas desde a última consulta. Conduta mantida.",
    "Queixa principal avaliada. Exame físico sem alterações relevantes. Orientações fornecidas.",
    "Retorno para reavaliação. Evolução favorável. Solicitados exames de controle.",
    "Paciente em acompanhamento. Orientado sobre hábitos e retorno em 30 dias.",
    "Avaliação inicial realizada. Plano terapêutico discutido com o paciente.",
    "Sem queixas novas. Mantido acompanhamento de rotina.",
)
