"""
price_calculator.py
-------------------
Regras de cálculo da locação Office Total.

A partir do custo:
    preco_36m = custo × coeficiente_36m
    preco_24m = preco_36m × 1.10
    preco_12m = preco_24m × 1.10
    preco_48m = preco_36m × 0.90
    preco_60m = preco_48m × 0.90

Cálculo reverso:
    custo_estimado = preco_36m / coeficiente_36m
"""

from typing import Dict

DEFAULT_COEFFICIENT_36M = 0.065

# Fatores de ajuste por prazo (sempre derivados do preço de 36 meses).
_FACTOR_24M = 1.10
_FACTOR_12M = 1.10   # aplicado sobre o de 24 meses
_FACTOR_48M = 0.90
_FACTOR_60M = 0.90   # aplicado sobre o de 48 meses


# --------------------------------------------------------------------------- #
# Validações                                                                  #
# --------------------------------------------------------------------------- #
def _require_positive(value, field_name: str) -> float:
    """Garante que o valor exista e seja estritamente positivo."""
    if value is None or value == "":
        raise ValueError(f"O campo '{field_name}' está vazio.")
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"O campo '{field_name}' não é um número válido.")
    if v == 0:
        raise ValueError(f"O campo '{field_name}' não pode ser zero.")
    if v < 0:
        raise ValueError(f"O campo '{field_name}' não pode ser negativo.")
    return v


def _terms_from_36m(preco_36m: float) -> Dict[str, float]:
    """Calcula 24, 12, 48 e 60 meses a partir do preço de 36 meses (já validado)."""
    preco_24m = round(preco_36m * _FACTOR_24M, 2)
    preco_12m = round(preco_24m * _FACTOR_12M, 2)
    preco_48m = round(preco_36m * _FACTOR_48M, 2)
    preco_60m = round(preco_48m * _FACTOR_60M, 2)
    return {
        "preco_12m": preco_12m,
        "preco_24m": preco_24m,
        "preco_36m": round(preco_36m, 2),
        "preco_48m": preco_48m,
        "preco_60m": preco_60m,
    }


# --------------------------------------------------------------------------- #
# Funções públicas                                                            #
# --------------------------------------------------------------------------- #
def calculate_prices_from_cost(
    cost: float, coefficient_36m: float = DEFAULT_COEFFICIENT_36M
) -> Dict[str, float]:
    """
    Calcula os preços de locação (12, 24, 36, 48, 60 meses) a partir do custo.

    Retorna um dicionário com as chaves:
        preco_12m, preco_24m, preco_36m, preco_48m, preco_60m
    """
    cost = _require_positive(cost, "Custo do equipamento")
    coef = _require_positive(coefficient_36m, "Coeficiente 36 meses")
    preco_36m = cost * coef
    return _terms_from_36m(preco_36m)


def calculate_cost_from_36m_price(
    price_36m: float, coefficient_36m: float = DEFAULT_COEFFICIENT_36M
) -> float:
    """
    Cálculo reverso: estima a base/custo do equipamento a partir do preço de 36 meses.

        custo_estimado = preco_36m / coeficiente_36m
    """
    price_36m = _require_positive(price_36m, "Preço de 36 meses")
    coef = _require_positive(coefficient_36m, "Coeficiente 36 meses")
    return round(price_36m / coef, 2)


def calculate_prices_from_36m(price_36m: float) -> Dict[str, float]:
    """
    Calcula 12, 24, 48 e 60 meses a partir do preço de 36 meses informado.

    Retorna um dicionário com as cinco chaves de prazo (incluindo preco_36m).
    """
    price_36m = _require_positive(price_36m, "Preço de 36 meses")
    return _terms_from_36m(price_36m)
