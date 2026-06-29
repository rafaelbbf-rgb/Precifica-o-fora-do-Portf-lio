"""Testes das regras de cálculo (price_calculator).

Observação: os testes usam um coeficiente genérico (5%) de propósito — o
coeficiente comercial real é configurado fora do código (Secrets/ambiente) e
não aparece no repositório.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.price_calculator import (
    DEFAULT_COEFFICIENT_36M,
    calculate_prices_from_cost,
    calculate_cost_from_36m_price,
    calculate_prices_from_36m,
)

COEF = 0.05  # coeficiente genérico para os testes


# --------------------------------------------------------------------------- #
# Precificação a partir do custo                                              #
# --------------------------------------------------------------------------- #
def test_coeficiente_padrao_e_valido():
    assert 0 < DEFAULT_COEFFICIENT_36M < 1


def test_precos_a_partir_do_custo():
    """Custo 2000 com coeficiente 5%: 36m=100 e demais prazos derivados."""
    p = calculate_prices_from_cost(2000, coefficient_36m=COEF)
    assert p == {
        "preco_12m": 121.00,
        "preco_24m": 110.00,
        "preco_36m": 100.00,
        "preco_48m": 90.00,
        "preco_60m": 81.00,
    }


def test_precos_retorna_todas_as_chaves():
    p = calculate_prices_from_cost(5000, coefficient_36m=COEF)
    assert set(p.keys()) == {"preco_12m", "preco_24m", "preco_36m", "preco_48m", "preco_60m"}


def test_relacao_entre_prazos():
    p = calculate_prices_from_cost(10000, coefficient_36m=COEF)
    assert p["preco_24m"] == round(p["preco_36m"] * 1.10, 2)
    assert p["preco_12m"] == round(p["preco_24m"] * 1.10, 2)
    assert p["preco_48m"] == round(p["preco_36m"] * 0.90, 2)
    assert p["preco_60m"] == round(p["preco_48m"] * 0.90, 2)


def test_coeficiente_customizado():
    p = calculate_prices_from_cost(2000, coefficient_36m=0.04)
    assert p["preco_36m"] == 80.00


@pytest.mark.parametrize("valor_invalido", [0, -1, -3000, None, ""])
def test_custo_invalido_levanta_erro(valor_invalido):
    with pytest.raises(ValueError):
        calculate_prices_from_cost(valor_invalido, coefficient_36m=COEF)


@pytest.mark.parametrize("coef_invalido", [0, -0.1, None, ""])
def test_coeficiente_invalido_levanta_erro(coef_invalido):
    with pytest.raises(ValueError):
        calculate_prices_from_cost(3000, coefficient_36m=coef_invalido)


# --------------------------------------------------------------------------- #
# Cálculo reverso                                                             #
# --------------------------------------------------------------------------- #
def test_custo_a_partir_do_preco_36m():
    assert calculate_cost_from_36m_price(100.00, coefficient_36m=COEF) == 2000.00


def test_custo_reverso_outro_coeficiente():
    assert calculate_cost_from_36m_price(80.00, coefficient_36m=0.04) == 2000.00


def test_ida_e_volta_consistente():
    p = calculate_prices_from_cost(7500, coefficient_36m=COEF)
    assert calculate_cost_from_36m_price(p["preco_36m"], coefficient_36m=COEF) == 7500.00


@pytest.mark.parametrize("preco_invalido", [0, -10, None, ""])
def test_preco_36m_invalido_levanta_erro(preco_invalido):
    with pytest.raises(ValueError):
        calculate_cost_from_36m_price(preco_invalido, coefficient_36m=COEF)


# --------------------------------------------------------------------------- #
# Prazos a partir do preço de 36m                                            #
# --------------------------------------------------------------------------- #
def test_prazos_a_partir_de_36m():
    p = calculate_prices_from_36m(100.00)
    assert p == {
        "preco_12m": 121.00,
        "preco_24m": 110.00,
        "preco_36m": 100.00,
        "preco_48m": 90.00,
        "preco_60m": 81.00,
    }


def test_from_cost_e_from_36m_coincidem():
    custo = calculate_prices_from_cost(3000, coefficient_36m=COEF)
    reverso = calculate_prices_from_36m(custo["preco_36m"])
    assert custo == reverso
