"""
ui_components.py
----------------
Componentes visuais (HTML) que dão à interface o acabamento premium da
Office Total. Todas as funções renderizam diretamente no Streamlit.

IMPORTANTE: todo HTML é emitido "rente à esquerda" (sem indentação) para evitar
que o Streamlit interprete o bloco como código e mostre as tags como texto.
"""

import base64
import os
from typing import Dict, List

from .formatting import format_brl

TERMOS = [
    ("12 meses", "preco_12m"),
    ("24 meses", "preco_24m"),
    ("36 meses", "preco_36m"),
    ("48 meses", "preco_48m"),
    ("60 meses", "preco_60m"),
]


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _logo_data_uri(filename: str = "logo.png") -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base, "assets", filename)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        encoded = base64.b64encode(fh.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def render_header(title: str, subtitle: str = "") -> None:
    import streamlit as st

    logo = _logo_data_uri("logo.png")
    img = f'<img src="{logo}" alt="Office Total"/>' if logo else ""
    html = (
        f'<div class="ot-header"><div>'
        f'<p class="ot-title">{title}</p>'
        f'<p class="ot-subtitle">{subtitle}</p>'
        f'</div>{img}</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_price_card(title: str, value: str, highlight: bool = False, badge: str = None) -> None:
    """Card de preço premium. `badge` mostra um selo no topo (ou None)."""
    import streamlit as st

    cls = "ot-price-card highlight" if highlight else "ot-price-card"
    badge_html = f'<span class="ot-badge">{badge}</span>' if badge else ""
    html = (
        f'<div class="{cls}">{badge_html}'
        f'<div class="ot-term">{title}</div>'
        f'<div class="ot-value">{value}</div>'
        f'<div class="ot-bar"></div></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_equipment_summary(data: Dict) -> None:
    """Resumo do equipamento (linha única) e, opcionalmente, responsável."""
    import streamlit as st

    def row(key: str, val: str) -> str:
        if not val:
            return ""
        return f'<div class="ot-row"><div class="ot-key">{key}</div><div class="ot-val">{val}</div></div>'

    linhas = row("Equipamento", data.get("equipamento", "")) + row("Responsável", data.get("responsavel", ""))
    if not linhas:
        linhas = '<div class="ot-row"><div class="ot-val">Nenhum dado informado.</div></div>'
    html = f'<div class="ot-summary"><h4>Resumo</h4>{linhas}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_items_table(itens: List[Dict], totals: Dict) -> None:
    """Tabela horizontal da proposta: itens nas linhas, prazos nas colunas."""
    import streamlit as st

    head = '<tr><th class="left">Descrição</th><th>Qtd</th>'
    head += "".join(f"<th>{rotulo}</th>" for rotulo, _ in TERMOS) + "</tr>"

    body = ""
    for it in itens:
        q = it.get("quantidade", 1)
        desc = it.get("descricao") or "—"
        if it.get("fixo"):
            val = format_brl(it["valores"]["preco_36m"] * q)
            body += (
                f'<tr class="fixed"><td class="left">{desc}</td><td>{q}</td>'
                f'<td class="fixedval" colspan="5">{val} · taxa fixa</td></tr>'
            )
        else:
            cells = ""
            for _, chave in TERMOS:
                cls = "col36" if chave == "preco_36m" else ""
                cells += f'<td class="{cls}">{format_brl(it["valores"][chave] * q)}</td>'
            body += f'<tr><td class="left">{desc}</td><td>{q}</td>{cells}</tr>'

    tcells = "".join(f"<td>{format_brl(totals[chave])}</td>" for _, chave in TERMOS)
    total_row = f'<tr class="total"><td class="left">Total mensal</td><td></td>{tcells}</tr>'

    html = f'<table class="ot-table"><thead>{head}</thead><tbody>{body}{total_row}</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)


def render_note(text: str, kind: str = "info") -> None:
    import streamlit as st

    icon = "ℹ️" if kind == "info" else "⚠️"
    html = f'<div class="ot-note {kind}"><span>{icon}</span><span>{text}</span></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_cost_proof_table(itens: List[Dict]) -> None:
    """
    Tabela interna para a aba "Comprovação de Custo": ao contrário de
    render_items_table (vendedor), aqui custo e coeficiente aparecem de
    propósito, além do status de evidência anexada por item.
    """
    import streamlit as st
    from . import theme

    head = (
        '<tr><th class="left">Descrição</th><th>Qtd</th><th>Custo unit.</th>'
        '<th>Coeficiente</th><th>36 meses</th><th class="left">Evidência</th></tr>'
    )
    body = ""
    for it in itens:
        q = it.get("quantidade", 1)
        desc = it.get("descricao") or "—"
        if it.get("fixo"):
            custo_str = "—"
            coef_str = "taxa fixa"
            preco36_str = f'{format_brl(it["valores"]["preco_36m"] * q)} · taxa fixa'
        else:
            custo_str = format_brl(it.get("custo", 0))
            coef = it.get("coef", 0)
            coef_str = f"{coef * 100:.2f}".rstrip("0").rstrip(".").replace(".", ",") + "%"
            preco36_str = format_brl(it["valores"]["preco_36m"] * q)
        n_evid = len(it.get("evidencias") or [])
        if n_evid:
            evid_str = f'<span style="color:{theme.SUCCESS_COLOR};font-weight:600">✓ {n_evid} anexo(s)</span>'
        else:
            evid_str = f'<span style="color:{theme.WARNING_COLOR};font-weight:700">✗ pendente</span>'
        body += (
            f'<tr><td class="left">{desc}</td><td>{q}</td><td>{custo_str}</td>'
            f'<td>{coef_str}</td><td class="col36">{preco36_str}</td>'
            f'<td class="left">{evid_str}</td></tr>'
        )
    html = f'<table class="ot-table"><thead>{head}</thead><tbody>{body}</tbody></table>'
    st.markdown(html, unsafe_allow_html=True)
