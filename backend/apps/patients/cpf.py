"""Normalização, validação e mascaramento de CPF."""

import re

_NON_DIGITS = re.compile(r"\D")
CPF_LENGTH = 11


def normalize_cpf(raw_cpf: str) -> str:
    """
    Remove pontuação do CPF.

    Exemplo:
        normalize_cpf("529.982.247-25")  # "52998224725"
    """
    return _NON_DIGITS.sub("", raw_cpf)


def is_valid_cpf(cpf_digits: str) -> bool:
    """
    Valida tamanho e dígitos verificadores de um CPF já normalizado.

    Exemplo:
        is_valid_cpf("52998224725")  # True
    """
    if len(cpf_digits) != CPF_LENGTH or not cpf_digits.isdigit():
        return False
    # Sequências repetidas (000..., 111...) passam no cálculo, mas não são CPFs válidos.
    if cpf_digits == cpf_digits[0] * CPF_LENGTH:
        return False
    return cpf_digits[9] == _check_digit(cpf_digits[:9]) and cpf_digits[10] == _check_digit(
        cpf_digits[:10]
    )


def mask_cpf(cpf_digits: str) -> str:
    """
    Oculta parte do CPF para listagens (LGPD: exposição mínima).

    Exemplo:
        mask_cpf("52998224725")  # "***.982.247-**"
    """
    if len(cpf_digits) != CPF_LENGTH:
        return ""
    return f"***.{cpf_digits[3:6]}.{cpf_digits[6:9]}-**"


def format_cpf(cpf_digits: str) -> str:
    """Formata CPF completo como 000.000.000-00."""
    if len(cpf_digits) != CPF_LENGTH:
        return cpf_digits
    return f"{cpf_digits[:3]}.{cpf_digits[3:6]}.{cpf_digits[6:9]}-{cpf_digits[9:]}"


def _check_digit(partial_cpf: str) -> str:
    weight_start = len(partial_cpf) + 1
    total = sum(
        int(digit) * weight
        for digit, weight in zip(partial_cpf, range(weight_start, 1, -1), strict=True)
    )
    remainder = (total * 10) % 11
    return str(0 if remainder == 10 else remainder)
