"""
formatting.py
-------------
Formatação e leitura de valores monetários no padrão brasileiro.

    format_brl(1234.56)        -> "R$ 1.234,56"
    parse_brl_currency("R$ 3.000,00") -> 3000.0
"""

from typing import Union


def format_brl(value: float) -> str:
    """Formata um número no padrão monetário brasileiro: R$ 1.234,56."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    # Formata em estilo US (1,234.56) e troca os separadores para o padrão BR.
    inteiro = f"{abs(value):,.2f}"
    inteiro = inteiro.replace(",", "X").replace(".", ",").replace("X", ".")
    sinal = "-" if value < 0 else ""
    return f"{sinal}R$ {inteiro}"


def parse_brl_currency(value: Union[str, int, float, None]) -> float:
    """
    Converte um valor digitado em real (com R$, ponto e/ou vírgula) em float.

    Aceita, por exemplo:
        "R$ 1.234,56" -> 1234.56
        "1.234,56"    -> 1234.56
        "1234,56"     -> 1234.56
        "3.000"       -> 3000.0   (ponto como separador de milhar)
        "12.50"       -> 12.5     (ponto como separador decimal)
        "1234"        -> 1234.0
        1234.5        -> 1234.5

    Lança ValueError quando o valor não pode ser interpretado.
    """
    if value is None:
        raise ValueError("Valor monetário vazio.")

    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip()
    if not s:
        raise ValueError("Valor monetário vazio.")

    # Remove símbolo, espaços (inclusive não separáveis) e qualquer caractere não numérico relevante.
    s = s.replace("R$", "").replace("r$", "").replace("\xa0", " ").strip()
    negativo = s.startswith("-")
    s = s.lstrip("+-").strip()

    has_comma = "," in s
    has_dot = "." in s

    if has_comma and has_dot:
        # O separador mais à direita é o decimal; o outro é separador de milhar.
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif has_comma:
        # Apenas vírgula -> decimal brasileiro.
        s = s.replace(",", ".")
    elif has_dot:
        # Apenas ponto: pode ser milhar (3.000) ou decimal (12.50).
        if s.count(".") > 1:
            s = s.replace(".", "")                      # vários pontos = milhar
        else:
            decimais = len(s.split(".")[1])
            if decimais == 3:
                s = s.replace(".", "")                  # "3.000" -> 3000 (milhar)
            # caso contrário, mantém como decimal ("12.50", "12.5")

    s = s.replace(" ", "")
    try:
        numero = float(s)
    except ValueError:
        raise ValueError(f"Valor monetário inválido: {value!r}")

    return -numero if negativo else numero
