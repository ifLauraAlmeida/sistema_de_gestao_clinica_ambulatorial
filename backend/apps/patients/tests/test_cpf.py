import pytest

from apps.patients.cpf import format_cpf, is_valid_cpf, mask_cpf, normalize_cpf
from apps.patients.tests.factories import build_fake_cpf


def test_normalize_removes_punctuation():
    assert normalize_cpf("123.456.789-09") == "12345678909"


def test_generated_fake_cpf_is_valid():
    assert is_valid_cpf(build_fake_cpf("100200300"))


@pytest.mark.parametrize("cpf", ["", "123", "11111111111", "12345678900", "abcdefghijk"])
def test_invalid_cpfs_are_rejected(cpf):
    assert not is_valid_cpf(cpf)


def test_mask_hides_first_and_last_digits():
    assert mask_cpf("12345678909") == "***.456.789-**"


def test_format_adds_punctuation():
    assert format_cpf("12345678909") == "123.456.789-09"
