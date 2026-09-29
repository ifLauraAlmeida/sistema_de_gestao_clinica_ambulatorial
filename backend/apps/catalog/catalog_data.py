"""
Catálogo inicial de serviços da clínica.

Organização definida pela clínica: área → grupo → serviço. Durações e preparos
são valores iniciais sugeridos e devem ser revisados pelo gestor no /admin;
preços não são definidos aqui.

"Pesquisa de refluxo" não foi cadastrada: depende do nome técnico do exame
realizado pela clínica (pHmetria, impedanciopHmetria ou outro).
"""

from dataclasses import dataclass, field

from apps.catalog.models import FormFieldType, SampleType, ServiceType

F = FormFieldType
C = ServiceType.CONSULTA
S = ServiceType.SESSAO
P = ServiceType.PROCEDIMENTO
E = ServiceType.EXAME


@dataclass(frozen=True)
class FieldSpec:
    key: str
    label: str
    field_type: FormFieldType
    unit: str = ""
    options: tuple[str, ...] = ()
    required: bool = False


@dataclass(frozen=True)
class ServiceSpec:
    name: str
    service_type: ServiceType | None = None
    duration: int | None = None
    laterality: bool = False
    sedation: bool = False
    laboratory: bool = False
    form: str | None = None
    preparation: str = ""
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class GroupSpec:
    """Grupo com valores padrão aplicados aos serviços que não os sobrescrevem."""

    name: str
    specialty_prefix: str
    service_type: ServiceType
    duration: int
    services: tuple[ServiceSpec | str, ...]
    form: str | None = None
    laterality: bool = False


@dataclass(frozen=True)
class CategorySpec:
    name: str
    groups: tuple[GroupSpec, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class LaboratoryExamSpec:
    name: str
    group: str
    sample_type: SampleType = SampleType.SANGUE
    fasting_hours: int = 0
    preparation: str = ""


@dataclass(frozen=True)
class PackageSpec:
    name: str
    description: str
    services: tuple[str, ...]
    laboratory_exams: tuple[str, ...]


SPECIALTIES: tuple[tuple[str, str], ...] = (
    ("Nutrição", "NUTR"),
    ("Odontologia", "ODON"),
    ("Oftalmologia", "OFTA"),
    ("Ortopedia", "ORTO"),
    ("Otorrinolaringologia", "OTOR"),
    ("Pediatria", "PEDI"),
    ("Pneumologia", "PNEU"),
    ("Proctologia", "PROC"),
    ("Psicologia", "PSIC"),
    ("Urologia", "UROL"),
    ("Audiologia", "AUDIO"),
    ("Cardiologia", "CARD"),
    ("Neurofisiologia", "NEUR"),
    ("Endoscopia", "ENDO"),
    ("Densitometria", "DENS"),
    ("Mamografia", "MAMO"),
    ("Radiologia", "RX"),
    ("Ultrassonografia", "USG"),
    ("Doppler vascular", "DOP"),
    ("Laboratório", "LAB"),
)

_OBS = FieldSpec("observacoes", "Observações", F.TEXTAREA)

FORM_TEMPLATES: dict[str, tuple[FieldSpec, ...]] = {
    "Avaliação nutricional": (
        FieldSpec("peso", "Peso", F.NUMBER, "kg", required=True),
        FieldSpec("altura", "Altura", F.NUMBER, "cm", required=True),
        FieldSpec("circunferencia_cintura", "Circunferência da cintura", F.NUMBER, "cm"),
        FieldSpec("circunferencia_quadril", "Circunferência do quadril", F.NUMBER, "cm"),
        _OBS,
    ),
    "Bioimpedância": (
        FieldSpec("peso", "Peso", F.NUMBER, "kg", required=True),
        FieldSpec("altura", "Altura", F.NUMBER, "cm", required=True),
        FieldSpec("gordura_corporal", "Gordura corporal", F.NUMBER, "%"),
        FieldSpec("massa_magra", "Massa magra", F.NUMBER, "kg"),
        FieldSpec("agua_corporal", "Água corporal", F.NUMBER, "%"),
        FieldSpec("taxa_metabolica_basal", "Taxa metabólica basal", F.NUMBER, "kcal"),
        _OBS,
    ),
    "Procedimento odontológico": (
        FieldSpec("dentes_regiao", "Dente(s) / região", F.TEXT, required=True),
        FieldSpec("material", "Material utilizado", F.TEXT),
        FieldSpec("anestesia", "Anestesia local", F.BOOLEAN),
        _OBS,
    ),
    "Exame oftalmológico": (
        FieldSpec("acuidade_od", "Acuidade visual OD", F.TEXT),
        FieldSpec("acuidade_oe", "Acuidade visual OE", F.TEXT),
        FieldSpec("pressao_od", "Pressão intraocular OD", F.NUMBER, "mmHg"),
        FieldSpec("pressao_oe", "Pressão intraocular OE", F.NUMBER, "mmHg"),
        _OBS,
    ),
    "Imobilização": (
        FieldSpec(
            "tipo",
            "Tipo",
            F.SELECT,
            options=("Gesso", "Tala gessada", "Órtese", "Enfaixamento"),
            required=True,
        ),
        FieldSpec("segmento", "Segmento imobilizado", F.TEXT, required=True),
        _OBS,
    ),
    "Procedimento ambulatorial": (
        FieldSpec("descricao", "Descrição do procedimento", F.TEXTAREA, required=True),
        FieldSpec("intercorrencias", "Houve intercorrências?", F.BOOLEAN),
        _OBS,
    ),
    "Audiometria": (
        FieldSpec("meatoscopia", "Meatoscopia", F.SELECT, options=("Normal", "Alterada")),
        FieldSpec("resultado_od", "Resultado orelha direita", F.TEXTAREA, required=True),
        FieldSpec("resultado_oe", "Resultado orelha esquerda", F.TEXTAREA, required=True),
        _OBS,
    ),
    "Imitanciometria": (
        FieldSpec(
            "curva_od", "Curva timpanométrica OD", F.SELECT, options=("A", "As", "Ad", "B", "C")
        ),
        FieldSpec(
            "curva_oe", "Curva timpanométrica OE", F.SELECT, options=("A", "As", "Ad", "B", "C")
        ),
        FieldSpec("reflexos_presentes", "Reflexos acústicos presentes", F.BOOLEAN),
        _OBS,
    ),
    "Eletrocardiograma": (
        FieldSpec("ritmo", "Ritmo", F.TEXT),
        FieldSpec("frequencia_cardiaca", "Frequência cardíaca", F.NUMBER, "bpm"),
        _OBS,
    ),
    "Teste ergométrico": (
        FieldSpec(
            "protocolo",
            "Protocolo",
            F.SELECT,
            options=("Bruce", "Bruce modificado", "Ellestad", "Rampa"),
            required=True,
        ),
        FieldSpec("tempo_exercicio", "Tempo de exercício", F.NUMBER, "min"),
        FieldSpec("fc_maxima", "FC máxima atingida", F.NUMBER, "bpm"),
        FieldSpec("pa_pico", "PA no pico do esforço", F.TEXT, "mmHg"),
        FieldSpec("motivo_interrupcao", "Motivo da interrupção", F.TEXT),
        _OBS,
    ),
    "MAPA": (
        FieldSpec("horario_instalacao", "Horário de instalação", F.TIME, required=True),
        FieldSpec("horario_retirada", "Horário de retirada", F.TIME),
        _OBS,
    ),
    "Eletroencefalograma": (
        FieldSpec("estado", "Estado", F.SELECT, options=("Vigília", "Sono", "Vigília e sono")),
        FieldSpec("fotoestimulacao", "Fotoestimulação realizada", F.BOOLEAN),
        FieldSpec("hiperventilacao", "Hiperventilação realizada", F.BOOLEAN),
        FieldSpec("intercorrencias", "Intercorrências", F.TEXTAREA),
    ),
    "Espirometria": (
        FieldSpec("vef1", "VEF1", F.NUMBER, "L"),
        FieldSpec("cvf", "CVF", F.NUMBER, "L"),
        FieldSpec("vef1_cvf", "VEF1/CVF", F.NUMBER, "%"),
        FieldSpec("broncodilatador", "Broncodilatador aplicado", F.BOOLEAN),
        _OBS,
    ),
    "Endoscopia": (
        FieldSpec("achados", "Achados", F.TEXTAREA, required=True),
        FieldSpec("biopsia", "Biópsia realizada", F.BOOLEAN),
        FieldSpec(
            "teste_urease",
            "Teste de urease",
            F.SELECT,
            options=("Não realizado", "Positivo", "Negativo"),
        ),
        FieldSpec("sedacao", "Sedação aplicada", F.BOOLEAN),
        FieldSpec("conclusao", "Conclusão", F.TEXTAREA),
    ),
    "Densitometria": (
        FieldSpec("t_score_coluna", "T-score coluna", F.NUMBER),
        FieldSpec("t_score_femur", "T-score fêmur", F.NUMBER),
        _OBS,
    ),
    "Mamografia": (
        FieldSpec("incidencias", "Incidências realizadas", F.TEXT, required=True),
        FieldSpec("exposicoes", "Número de exposições", F.NUMBER),
        FieldSpec("protese", "Paciente com prótese mamária", F.BOOLEAN),
        _OBS,
    ),
    "Radiografia": (
        FieldSpec("incidencias", "Incidências realizadas", F.TEXT, required=True),
        FieldSpec("exposicoes", "Número de exposições", F.NUMBER),
        FieldSpec("repeticao", "Houve repetição?", F.BOOLEAN),
        FieldSpec("motivo_repeticao", "Motivo da repetição", F.TEXT),
        _OBS,
    ),
    "Laudo de imagem": (
        FieldSpec("achados", "Achados", F.TEXTAREA, required=True),
        FieldSpec("conclusao", "Conclusão", F.TEXTAREA, required=True),
    ),
    "Coleta laboratorial": (
        FieldSpec("amostras_coletadas", "Amostras coletadas", F.TEXT, required=True),
        FieldSpec("jejum_horas", "Jejum informado", F.NUMBER, "h"),
        FieldSpec("intercorrencias", "Intercorrências na coleta", F.TEXTAREA),
    ),
}

_JEJUM_8H = "Jejum de 8 horas."
_BEXIGA_CHEIA = "Bexiga cheia: beber 1 litro de água 1 hora antes e não urinar."


def _consultations(specialty: str, prefix: str, extras: tuple[ServiceSpec | str, ...]) -> GroupSpec:
    """Grupo de consulta padrão: primeira consulta, retorno e serviços da especialidade."""
    return GroupSpec(
        specialty,
        prefix,
        C,
        30,
        (
            f"Consulta {_CONSULTATION_ADJECTIVE[specialty]} — primeira consulta",
            ServiceSpec(f"Consulta {_CONSULTATION_ADJECTIVE[specialty]} — retorno", duration=20),
            *extras,
        ),
    )


_CONSULTATION_ADJECTIVE = {
    "Oftalmologia": "oftalmológica",
    "Ortopedia": "ortopédica",
    "Otorrinolaringologia": "de otorrinolaringologia",
    "Pediatria": "pediátrica",
    "Pneumologia": "pneumológica",
    "Proctologia": "proctológica",
    "Urologia": "urológica",
}

CATALOG: tuple[CategorySpec, ...] = (
    CategorySpec(
        "Consultas e atendimentos",
        (
            GroupSpec(
                "Nutrição",
                "NUTR",
                C,
                45,
                (
                    "Consulta de Nutrição — primeira consulta",
                    ServiceSpec("Consulta de Nutrição — retorno", duration=30),
                    ServiceSpec("Avaliação nutricional", C, form="Avaliação nutricional"),
                    ServiceSpec("Avaliação antropométrica", C, 30, form="Avaliação nutricional"),
                    ServiceSpec(
                        "Bioimpedância",
                        E,
                        20,
                        form="Bioimpedância",
                        preparation="Jejum de 4 horas; não praticar exercícios nem ingerir "
                        "café ou álcool nas 24 horas anteriores.",
                    ),
                    ServiceSpec("Bioimpedância + avaliação nutricional", E, form="Bioimpedância"),
                    ServiceSpec("Avaliação de composição corporal", E, 30, form="Bioimpedância"),
                ),
            ),
            GroupSpec(
                "Odontologia",
                "ODON",
                P,
                40,
                (
                    ServiceSpec("Consulta odontológica — avaliação", C, 30),
                    ServiceSpec("Consulta odontológica — retorno", C, 20),
                    ServiceSpec("Atendimento odontológico de urgência", P, 40),
                    "Profilaxia / limpeza dentária",
                    ServiceSpec("Aplicação de flúor", duration=20),
                    ServiceSpec("Raspagem periodontal", duration=60),
                    ServiceSpec("Restauração dentária", duration=60),
                    ServiceSpec("Extração dentária simples", duration=60),
                    ServiceSpec("Curativo odontológico", duration=30),
                    ServiceSpec("Avaliação periodontal", C, 30),
                ),
                form="Procedimento odontológico",
            ),
            _consultations(
                "Oftalmologia",
                "OFTA",
                (
                    ServiceSpec("Avaliação de acuidade visual", E, 15, form="Exame oftalmológico"),
                    ServiceSpec("Refração", E, 20, form="Exame oftalmológico"),
                    ServiceSpec("Tonometria", E, 15, form="Exame oftalmológico"),
                    ServiceSpec("Biomicroscopia", E, 20, form="Exame oftalmológico"),
                    ServiceSpec(
                        "Fundoscopia / exame de fundo de olho",
                        E,
                        30,
                        form="Exame oftalmológico",
                        preparation="Pode haver dilatação da pupila: vir acompanhado e não "
                        "dirigir após o exame.",
                        aliases=("Mapeamento de retina",),
                    ),
                    ServiceSpec(
                        "Avaliação oftalmológica completa", E, 60, form="Exame oftalmológico"
                    ),
                ),
            ),
            _consultations(
                "Ortopedia",
                "ORTO",
                (
                    ServiceSpec("Avaliação ortopédica"),
                    ServiceSpec(
                        "Imobilização ortopédica", P, 30, laterality=True, form="Imobilização"
                    ),
                    ServiceSpec(
                        "Retirada de imobilização", P, 20, laterality=True, form="Imobilização"
                    ),
                ),
            ),
            _consultations(
                "Otorrinolaringologia",
                "OTOR",
                (
                    ServiceSpec("Avaliação otológica"),
                    ServiceSpec(
                        "Remoção de cerúmen",
                        P,
                        20,
                        laterality=True,
                        form="Procedimento ambulatorial",
                    ),
                    ServiceSpec("Avaliação nasal"),
                    ServiceSpec("Avaliação da garganta/laringe"),
                ),
            ),
            _consultations(
                "Pediatria",
                "PEDI",
                (
                    ServiceSpec("Consulta pediátrica de acompanhamento", C, 30),
                    ServiceSpec("Avaliação de crescimento e desenvolvimento", C, 30),
                ),
            ),
            _consultations("Pneumologia", "PNEU", (ServiceSpec("Avaliação pneumológica"),)),
            _consultations(
                "Proctologia",
                "PROC",
                (
                    ServiceSpec("Avaliação proctológica"),
                    ServiceSpec(
                        "Anuscopia",
                        E,
                        20,
                        form="Procedimento ambulatorial",
                        preparation="Evacuar antes do exame; seguir orientação médica sobre "
                        "preparo intestinal.",
                    ),
                ),
            ),
            GroupSpec(
                "Psicologia",
                "PSIC",
                S,
                50,
                (
                    ServiceSpec("Avaliação psicológica inicial", S, 60),
                    "Sessão de psicologia individual",
                    "Sessão de acompanhamento psicológico",
                    ServiceSpec("Consulta/devolutiva psicológica", S, 50),
                ),
            ),
            _consultations("Urologia", "UROL", (ServiceSpec("Avaliação urológica"),)),
        ),
    ),
    CategorySpec(
        "Audiologia",
        (
            GroupSpec(
                "Audiometria",
                "AUDIO",
                E,
                30,
                (
                    "Audiometria tonal limiar",
                    "Audiometria vocal",
                    ServiceSpec("Audiometria tonal + vocal", duration=40),
                    "Audiometria ocupacional",
                    ServiceSpec("Audiometria infantil", duration=40),
                ),
                form="Audiometria",
            ),
            GroupSpec(
                "Imitanciometria",
                "AUDIO",
                E,
                20,
                (
                    "Timpanometria",
                    "Pesquisa de reflexos acústicos",
                    "Timpanometria + reflexos acústicos",
                    ServiceSpec("Imitanciometria completa", aliases=("Impedanciometria",)),
                ),
                form="Imitanciometria",
            ),
        ),
    ),
    CategorySpec(
        "Cardiologia",
        (
            GroupSpec(
                "Eletrocardiograma",
                "CARD",
                E,
                15,
                (
                    ServiceSpec(
                        "Eletrocardiograma de repouso — ECG 12 derivações", aliases=("ECG",)
                    ),
                    "Eletrocardiograma pediátrico",
                ),
                form="Eletrocardiograma",
            ),
            GroupSpec(
                "Ecocardiograma",
                "CARD",
                E,
                40,
                (
                    ServiceSpec("Ecocardiograma transtorácico", aliases=("Ecocardiograma",)),
                    "Ecocardiograma transtorácico com Doppler",
                    "Ecocardiograma com Doppler colorido",
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Ergometria",
                "CARD",
                E,
                45,
                (
                    ServiceSpec(
                        "Teste ergométrico",
                        preparation="Roupa e tênis confortáveis; refeição leve 2 horas antes; "
                        "não fumar no dia do exame.",
                        aliases=(
                            "Ergometria",
                            "Teste ergométrico em esteira",
                            "Teste ergométrico com ECG de esforço",
                            "Teste de esforço",
                        ),
                    ),
                ),
                form="Teste ergométrico",
            ),
            GroupSpec(
                "MAPA",
                "CARD",
                E,
                20,
                (
                    # Instalação e retirada são etapas registradas no formulário, não serviços.
                    ServiceSpec(
                        "MAPA 24 horas",
                        preparation="Tomar banho antes; usar roupa de manga larga; manter "
                        "a rotina e anotar atividades durante o exame.",
                        aliases=("MAPA — pressão arterial 24 horas", "Instalação do MAPA"),
                    ),
                ),
                form="MAPA",
            ),
        ),
    ),
    CategorySpec(
        "Neurologia / Neurofisiologia",
        (
            GroupSpec(
                "Eletroencefalografia",
                "NEUR",
                E,
                60,
                (
                    "EEG em vigília",
                    "EEG com sono",
                    ServiceSpec(
                        "EEG com privação de sono",
                        preparation="Dormir no máximo 4 horas na noite anterior; cabelo limpo "
                        "e seco, sem cremes.",
                    ),
                    "EEG com fotoestimulação",
                    "EEG com hiperventilação",
                    ServiceSpec("EEG com mapeamento cerebral", aliases=("Mapeamento cerebral",)),
                ),
                form="Eletroencefalograma",
            ),
        ),
    ),
    CategorySpec(
        "Pneumologia",
        (
            GroupSpec(
                "Prova de função pulmonar",
                "PNEU",
                E,
                30,
                (
                    "Espirometria simples",
                    "Espirometria pré-broncodilatador",
                    ServiceSpec("Espirometria pré e pós-broncodilatador", duration=45),
                    ServiceSpec("Prova de função pulmonar completa", duration=60),
                ),
                form="Espirometria",
            ),
        ),
    ),
    CategorySpec(
        "Endoscopia",
        (
            GroupSpec(
                "Endoscopia digestiva alta",
                "ENDO",
                E,
                30,
                tuple(
                    ServiceSpec(
                        name,
                        sedation=True,
                        preparation="Jejum de 8 horas (inclusive água). Com sedação, vir "
                        "acompanhado de um adulto e não dirigir no dia.",
                    )
                    for name in (
                        "Endoscopia digestiva alta",
                        "Endoscopia digestiva alta com biópsia",
                        "Endoscopia digestiva alta com teste de urease",
                        "Endoscopia digestiva alta + biópsia + teste de urease",
                    )
                ),
                form="Endoscopia",
            ),
        ),
    ),
    CategorySpec(
        "Densitometria óssea",
        (
            GroupSpec(
                "Densitometria",
                "DENS",
                E,
                20,
                (
                    "Densitometria óssea — coluna lombar",
                    ServiceSpec("Densitometria óssea — fêmur", laterality=True),
                    "Densitometria óssea — coluna + fêmur",
                    ServiceSpec("Densitometria óssea de corpo inteiro", duration=30),
                    ServiceSpec("Avaliação de composição corporal por densitometria", duration=30),
                ),
                form="Densitometria",
            ),
        ),
    ),
    CategorySpec(
        "Mamografia",
        (
            GroupSpec(
                "Mamografia",
                "MAMO",
                E,
                20,
                tuple(
                    ServiceSpec(
                        name,
                        laterality=name == "Mamografia unilateral",
                        preparation="Não usar desodorante, talco ou creme nas mamas e axilas "
                        "no dia do exame; trazer exames anteriores.",
                    )
                    for name in (
                        "Mamografia bilateral",
                        "Mamografia unilateral",
                        "Mamografia de rastreamento",
                        "Mamografia diagnóstica",
                        "Mamografia em paciente com prótese mamária",
                        "Incidências complementares",
                    )
                ),
                form="Mamografia",
            ),
        ),
    ),
    CategorySpec(
        "Raios-X",
        (
            GroupSpec(
                "Cabeça e face",
                "RX",
                E,
                15,
                (
                    "Raio-X de crânio",
                    "Raio-X de seios da face",
                    "Raio-X de ossos da face",
                    "Raio-X de ossos nasais",
                    "Raio-X de mandíbula",
                ),
                form="Radiografia",
            ),
            GroupSpec(
                "Coluna",
                "RX",
                E,
                15,
                (
                    "Raio-X de coluna cervical",
                    "Raio-X de coluna torácica",
                    "Raio-X de coluna lombar",
                    "Raio-X de coluna lombossacra",
                    "Raio-X de sacro",
                    "Raio-X de cóccix",
                    ServiceSpec("Raio-X panorâmico da coluna", duration=20),
                    ServiceSpec("Raio-X para avaliação de escoliose", duration=20),
                ),
                form="Radiografia",
            ),
            GroupSpec(
                "Tórax",
                "RX",
                E,
                15,
                (
                    "Raio-X de tórax PA",
                    "Raio-X de tórax PA + perfil",
                    ServiceSpec("Raio-X de costelas", laterality=True),
                    "Raio-X de esterno",
                ),
                form="Radiografia",
            ),
            GroupSpec(
                "Abdome e pelve",
                "RX",
                E,
                15,
                (
                    "Raio-X de abdome",
                    "Raio-X de abdome simples",
                    "Raio-X de pelve",
                    "Raio-X de bacia",
                ),
                form="Radiografia",
            ),
            GroupSpec(
                "Membro superior",
                "RX",
                E,
                15,
                (
                    "Raio-X de clavícula",
                    "Raio-X de ombro",
                    "Raio-X de úmero",
                    "Raio-X de cotovelo",
                    "Raio-X de antebraço",
                    "Raio-X de punho",
                    "Raio-X de mão",
                    "Raio-X de dedo da mão",
                ),
                form="Radiografia",
                laterality=True,
            ),
            GroupSpec(
                "Membro inferior",
                "RX",
                E,
                15,
                (
                    "Raio-X de quadril",
                    "Raio-X de fêmur",
                    "Raio-X de joelho",
                    "Raio-X de patela",
                    "Raio-X de perna",
                    "Raio-X de tornozelo",
                    "Raio-X de pé",
                    "Raio-X de calcâneo",
                    "Raio-X de dedo do pé",
                ),
                form="Radiografia",
                laterality=True,
            ),
            GroupSpec(
                "Pediátricos/especiais",
                "RX",
                E,
                15,
                (
                    "Raio-X para idade óssea",
                    ServiceSpec("Raio-X panorâmico de membros inferiores", duration=20),
                ),
                form="Radiografia",
            ),
        ),
    ),
    CategorySpec(
        "Ultrassonografia",
        (
            GroupSpec(
                "Abdome",
                "USG",
                E,
                30,
                (
                    ServiceSpec(
                        "Ultrassonografia de abdome total",
                        preparation=f"{_JEJUM_8H} {_BEXIGA_CHEIA}",
                    ),
                    ServiceSpec("Ultrassonografia de abdome superior", preparation=_JEJUM_8H),
                    "Ultrassonografia de parede abdominal",
                    ServiceSpec("Ultrassonografia de região inguinal", laterality=True),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Sistema urinário",
                "USG",
                E,
                30,
                tuple(
                    ServiceSpec(name, preparation=_BEXIGA_CHEIA)
                    for name in (
                        "Ultrassonografia de rins",
                        "Ultrassonografia de rins e vias urinárias",
                        "Ultrassonografia de bexiga",
                        "Ultrassonografia do aparelho urinário",
                    )
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Pelve / ginecologia",
                "USG",
                E,
                30,
                (
                    ServiceSpec("Ultrassonografia pélvica", preparation=_BEXIGA_CHEIA),
                    ServiceSpec(
                        "Ultrassonografia transvaginal", preparation="Esvaziar a bexiga antes."
                    ),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Obstetrícia",
                "USG",
                E,
                30,
                (
                    "Ultrassonografia obstétrica",
                    ServiceSpec("Ultrassonografia obstétrica com Doppler", duration=40),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Mama",
                "USG",
                E,
                30,
                (
                    "Ultrassonografia mamária bilateral",
                    ServiceSpec("Ultrassonografia mamária unilateral", laterality=True),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Tireoide e pescoço",
                "USG",
                E,
                30,
                (
                    "Ultrassonografia de tireoide",
                    ServiceSpec("Ultrassonografia de tireoide com Doppler", duration=40),
                    "Ultrassonografia cervical",
                    "Ultrassonografia de partes moles do pescoço",
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Urologia masculina",
                "USG",
                E,
                30,
                (
                    ServiceSpec(
                        "Ultrassonografia de próstata via abdominal", preparation=_BEXIGA_CHEIA
                    ),
                    ServiceSpec(
                        "Ultrassonografia de próstata transretal",
                        preparation="Realizar lavagem intestinal conforme orientação.",
                    ),
                    "Ultrassonografia de bolsa escrotal",
                    "Ultrassonografia testicular",
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Partes moles",
                "USG",
                E,
                30,
                (
                    "Ultrassonografia de partes moles",
                    ServiceSpec("Ultrassonografia de região específica", laterality=True),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Musculoesquelético",
                "USG",
                E,
                30,
                (
                    "Ultrassonografia de ombro",
                    "Ultrassonografia de cotovelo",
                    "Ultrassonografia de punho",
                    "Ultrassonografia de mão",
                    "Ultrassonografia de quadril",
                    "Ultrassonografia de joelho",
                    "Ultrassonografia de tornozelo",
                    "Ultrassonografia de pé",
                ),
                form="Laudo de imagem",
                laterality=True,
            ),
        ),
    ),
    CategorySpec(
        "Doppler",
        (
            GroupSpec(
                "Doppler arterial",
                "DOP",
                E,
                40,
                (
                    ServiceSpec("Doppler arterial de membro superior", laterality=True),
                    ServiceSpec("Doppler arterial de membros superiores", duration=60),
                    ServiceSpec("Doppler arterial de membro inferior", laterality=True),
                    ServiceSpec("Doppler arterial de membros inferiores", duration=60),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Doppler venoso",
                "DOP",
                E,
                40,
                (
                    ServiceSpec("Doppler venoso de membro superior", laterality=True),
                    ServiceSpec("Doppler venoso de membros superiores", duration=60),
                    ServiceSpec("Doppler venoso de membro inferior", laterality=True),
                    ServiceSpec("Doppler venoso de membros inferiores", duration=60),
                ),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Vasos cervicais",
                "DOP",
                E,
                40,
                ("Doppler de carótidas", "Doppler de carótidas e vertebrais"),
                form="Laudo de imagem",
            ),
            GroupSpec(
                "Outros",
                "DOP",
                E,
                40,
                (
                    ServiceSpec("Doppler de aorta", preparation=_JEJUM_8H),
                    ServiceSpec("Doppler de artérias renais", preparation=_JEJUM_8H),
                    ServiceSpec("Doppler de vasos abdominais", preparation=_JEJUM_8H),
                    "Doppler de bolsa escrotal",
                    "Doppler de tireoide",
                    "Doppler obstétrico",
                ),
                form="Laudo de imagem",
            ),
        ),
    ),
    CategorySpec(
        "Laboratório",
        (
            GroupSpec(
                "Coleta",
                "LAB",
                E,
                10,
                (
                    ServiceSpec(
                        "Coleta de exames laboratoriais",
                        laboratory=True,
                        preparation="Seguir o preparo de cada exame solicitado (jejum, "
                        "primeira urina da manhã etc.).",
                        aliases=("Laboratório", "Análises clínicas", "Exame de sangue"),
                    ),
                ),
                form="Coleta laboratorial",
            ),
        ),
    ),
)

_SANGUE = SampleType.SANGUE
_URINA_MANHA = "Primeira urina da manhã, jato médio, em frasco estéril."

LABORATORY_EXAMS: tuple[LaboratoryExamSpec, ...] = (
    *(
        LaboratoryExamSpec(name, "Hematologia")
        for name in (
            "Hemograma completo",
            "Hematócrito",
            "Hemoglobina",
            "Contagem de plaquetas",
            "VHS",
        )
    ),
    LaboratoryExamSpec("Glicemia de jejum", "Glicemia e metabolismo", fasting_hours=8),
    LaboratoryExamSpec("Hemoglobina glicada", "Glicemia e metabolismo"),
    LaboratoryExamSpec("Insulina", "Glicemia e metabolismo", fasting_hours=8),
    LaboratoryExamSpec(
        "Curva glicêmica",
        "Glicemia e metabolismo",
        fasting_hours=8,
        preparation="Permanecer cerca de 2 horas no laboratório.",
    ),
    LaboratoryExamSpec(
        "Curva insulinêmica",
        "Glicemia e metabolismo",
        fasting_hours=8,
        preparation="Permanecer cerca de 2 horas no laboratório.",
    ),
    *(
        LaboratoryExamSpec(name, "Perfil lipídico", fasting_hours=12)
        for name in ("Colesterol total", "HDL", "LDL", "VLDL", "Triglicerídeos")
    ),
    *(LaboratoryExamSpec(name, "Função renal") for name in ("Ureia", "Creatinina", "Ácido úrico")),
    *(
        LaboratoryExamSpec(name, "Função hepática")
        for name in (
            "TGO / AST",
            "TGP / ALT",
            "GGT",
            "Fosfatase alcalina",
            "Bilirrubina total",
            "Bilirrubinas e frações",
        )
    ),
    *(
        LaboratoryExamSpec(name, "Hormônios da tireoide")
        for name in ("TSH", "T4 livre", "T4 total", "T3", "Anticorpos tireoidianos")
    ),
    *(
        LaboratoryExamSpec(name, "Hormônios sexuais/reprodutivos")
        for name in (
            "FSH",
            "LH",
            "Estradiol",
            "Progesterona",
            "Prolactina",
            "Testosterona total",
            "Testosterona livre",
            "SHBG",
            "DHEA-S",
            "Beta-HCG",
        )
    ),
    LaboratoryExamSpec(
        "Cortisol", "Hormônios metabólicos/adrenais", preparation="Coleta pela manhã."
    ),
    LaboratoryExamSpec("ACTH", "Hormônios metabólicos/adrenais", preparation="Coleta pela manhã."),
    *(
        LaboratoryExamSpec(name, "Coagulação")
        for name in ("TAP / TP", "INR", "TTPa", "Coagulograma")
    ),
    LaboratoryExamSpec("Ferro sérico", "Vitaminas e minerais", fasting_hours=8),
    *(
        LaboratoryExamSpec(name, "Vitaminas e minerais")
        for name in (
            "Ferritina",
            "Transferrina",
            "Vitamina B12",
            "Ácido fólico",
            "Vitamina D",
            "Cálcio",
            "Magnésio",
        )
    ),
    LaboratoryExamSpec("EAS / urina tipo I", "Urina", SampleType.URINA, preparation=_URINA_MANHA),
    LaboratoryExamSpec("Urocultura", "Urina", SampleType.URINA, preparation=_URINA_MANHA),
    LaboratoryExamSpec("Proteinúria", "Urina", SampleType.URINA),
    LaboratoryExamSpec("Microalbuminúria", "Urina", SampleType.URINA),
    *(
        LaboratoryExamSpec(
            name, "Fezes", SampleType.FEZES, preparation="Coletar em frasco próprio fornecido."
        )
        for name in ("Parasitológico de fezes", "Pesquisa de sangue oculto", "Coprocultura")
    ),
    LaboratoryExamSpec("PSA total", "Marcadores prostáticos"),
    LaboratoryExamSpec("PSA livre", "Marcadores prostáticos"),
)

PACKAGES: tuple[PackageSpec, ...] = (
    PackageSpec(
        "Pacote preventivo feminino",
        "Check-up preventivo feminino. Itens ajustáveis pelo gestor.",
        services=(
            "Mamografia bilateral",
            "Ultrassonografia transvaginal",
            "Ultrassonografia mamária bilateral",
            "Coleta de exames laboratoriais",
        ),
        laboratory_exams=(
            "Hemograma completo",
            "Glicemia de jejum",
            "Colesterol total",
            "HDL",
            "LDL",
            "Triglicerídeos",
            "TSH",
            "EAS / urina tipo I",
        ),
    ),
    PackageSpec(
        "Pacote preventivo masculino",
        "Check-up preventivo masculino. Itens ajustáveis pelo gestor.",
        services=(
            "Consulta urológica — primeira consulta",
            "Avaliação urológica",
            "Ultrassonografia de próstata via abdominal",
            "Coleta de exames laboratoriais",
        ),
        laboratory_exams=(
            "Hemograma completo",
            "Glicemia de jejum",
            "Colesterol total",
            "HDL",
            "LDL",
            "Triglicerídeos",
            "PSA total",
            "PSA livre",
        ),
    ),
)
