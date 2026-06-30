"""Testes de formatação e leitura monetária (formatting)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.formatting import format_brl, parse_brl_currency


# --------------------------------------------------------------------------- #
# format_brl                                                                  #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("valor,esperado", [
    (1234.56, "R$ 1.234,56"),
    (195.00, "R$ 195,00"),
    (3000, "R$ 3.000,00"),
    (0, "R$ 0,00"),
    (1000000.5, "R$ 1.000.000,50"),
    (157.95, "R$ 157,95"),
])
def test_format_brl(valor, esperado):
    assert format_brl(valor) == esperado


def test_format_brl_negativo():
    assert format_brl(-1234.56) == "-R$ 1.234,56"


def test_format_brl_arredonda_centavos():
    assert format_brl(10.999) == "R$ 11,00"


def test_format_brl_entrada_invalida_vira_zero():
    assert format_brl("abc") == "R$ 0,00"


# --------------------------------------------------------------------------- #
# parse_brl_currency                                                          #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("entrada,esperado", [
    ("R$ 1.234,56", 1234.56),
    ("1.234,56", 1234.56),
    ("1234,56", 1234.56),
    ("R$ 3.000,00", 3000.00),
    ("3.000", 3000.0),          # ponto como separador de milhar
    ("12,50", 12.5),
    ("12.50", 12.5),            # ponto como separador decimal
    ("1234", 1234.0),
    ("1.234.567,89", 1234567.89),
    ("  R$  99,90 ", 99.90),
    (1500, 1500.0),
    (1500.75, 1500.75),
])
def test_parse_brl_currency(entrada, esperado):
    assert parse_brl_currency(entrada) == pytest.approx(esperado)


def test_parse_negativo():
    assert parse_brl_currency("-R$ 100,00") == pytest.approx(-100.0)


@pytest.mark.parametrize("entrada", [None, "", "   "])
def test_parse_vazio_levanta_erro(entrada):
    with pytest.raises(ValueError):
        parse_brl_currency(entrada)


def test_parse_texto_invalido_levanta_erro():
    with pytest.raises(ValueError):
        parse_brl_currency("R$ abc")


def test_ida_e_volta_format_parse():
    """parse(format(x)) deve retornar x."""
    for x in (195.00, 1234.56, 3000.0, 99.90):
        assert parse_brl_currency(format_brl(x)) == pytest.approx(x)
