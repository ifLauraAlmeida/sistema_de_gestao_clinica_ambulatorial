"""Valores fictícios plausíveis para os formulários de execução de procedimentos."""

import random

from apps.catalog.execution_forms import FormValue
from apps.catalog.models import ExecutionFormField, FormFieldType

# Faixas numéricas por chave de campo (mínimo, máximo, casas decimais).
_NUMBER_RANGES: dict[str, tuple[float, float, int]] = {
    "peso": (48, 110, 1),
    "altura": (150, 192, 0),
    "circunferencia_cintura": (62, 118, 0),
    "circunferencia_quadril": (84, 125, 0),
    "gordura_corporal": (14, 42, 1),
    "massa_magra": (38, 78, 1),
    "agua_corporal": (45, 65, 1),
    "taxa_metabolica_basal": (1150, 2100, 0),
    "exposicoes": (1, 3, 0),
    "t_score_coluna": (-3.2, 1.0, 1),
    "t_score_femur": (-2.8, 1.2, 1),
    "frequencia_cardiaca": (58, 96, 0),
    "jejum_horas": (0, 12, 0),
    "pressao_od": (11, 20, 0),
    "pressao_oe": (11, 20, 0),
}

_TEXT_VALUES: dict[str, tuple[str, ...]] = {
    "incidencias": ("AP e perfil", "PA", "AP, perfil e oblíqua", "Crânio-caudal e médio-lateral"),
    "amostras_coletadas": ("Sangue (2 tubos)", "Sangue (3 tubos) e urina", "Sangue (1 tubo)"),
    "dentes_regiao": ("Arcada superior", "Dente 36", "Dentes 14 e 15", "Arcada completa"),
    "material": ("Resina composta", "Pasta profilática", "Ionômero de vidro"),
    "segmento": ("Tornozelo", "Punho", "Joelho"),
    "ritmo": ("Sinusal",),
    "motivo_repeticao": ("",),
}

_LONG_TEXTS = (
    "Exame realizado sem intercorrências.",
    "Estruturas avaliadas dentro dos limites da normalidade.",
    "Achados discretos, sem sinais de gravidade. Correlacionar com a clínica.",
)


def fake_field_value(field: ExecutionFormField, rng: random.Random) -> FormValue:
    """
    Valor fictício compatível com o tipo e as opções do campo.

    Exemplo:
        fake_field_value(campo_peso, random.Random(1))  # 71.4
    """
    field_type = FormFieldType(field.field_type)
    if field_type == FormFieldType.NUMBER:
        low, high, digits = _NUMBER_RANGES.get(field.key, (1, 10, 0))
        return round(rng.uniform(low, high), digits)
    if field_type == FormFieldType.BOOLEAN:
        return rng.random() < 0.2
    if field_type == FormFieldType.SELECT:
        return rng.choice(field.options) if field.options else None
    if field_type == FormFieldType.TIME:
        return f"{rng.randint(7, 17):02d}:{rng.choice(('00', '15', '30', '45'))}"
    if field_type == FormFieldType.TEXTAREA:
        return rng.choice(_LONG_TEXTS)
    return rng.choice(_TEXT_VALUES.get(field.key, ("Registrado",))) or None
