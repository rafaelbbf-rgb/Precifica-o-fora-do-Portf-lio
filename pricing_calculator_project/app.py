"""
app.py
------
Calculadora Executiva de Precificação — Grupo Office Total.
Modelo multi-item: o gerente monta uma proposta com um ou mais itens
(por custo ou taxa fixa) e gera um PDF horizontal para o vendedor.

Execução:
    streamlit run app.py
"""

import os
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import theme
from src.auth import require_login, render_logout
from src.formatting import format_brl, parse_brl_currency
from src.price_calculator import (
    DEFAULT_COEFFICIENT_36M,
    calculate_prices_from_cost,
    calculate_cost_from_36m_price,
    calculate_prices_from_36m,
)
from src.report_generator import generate_executive_report, compute_totals
from src.cost_proof_generator import generate_cost_proof_report
from src.ui_components import (
    render_header,
    render_price_card,
    render_items_table,
    render_cost_proof_table,
    render_note,
)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "relatorios")
TERMOS = ["preco_12m", "preco_24m", "preco_36m", "preco_48m", "preco_60m"]


def get_default_coef_pct() -> float:
    """Coeficiente padrão (em %) lido dos Secrets/ambiente. Fora do código."""
    val = None
    try:
        if "default_coefficient_36m" in st.secrets:
            val = float(st.secrets["default_coefficient_36m"])
    except Exception:
        val = None
    if val is None:
        env = os.environ.get("DEFAULT_COEF")
        if env:
            try:
                val = float(env)
            except ValueError:
                val = None
    if val is None:
        val = DEFAULT_COEFFICIENT_36M  # placeholder genérico
    return round(val * 100, 4)


st.set_page_config(page_title="Precificação · Office Total", page_icon="💼", layout="wide")
theme.apply_office_total_theme()

# Proteção por senha (ativa apenas quando uma senha está configurada).
if not require_login():
    st.stop()

render_header(
    "Calculadora Executiva de Precificação",
    "Locação de equipamentos · Tecnologia por Assinatura",
)
render_logout()

if "itens" not in st.session_state:
    st.session_state["itens"] = []


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #
def _render_price_grid(precos: dict, badge_36m: str = "Plano recomendado") -> None:
    c = st.columns([1, 1, 1])
    with c[1]:
        render_price_card("36 meses", format_brl(precos["preco_36m"]), highlight=True, badge=badge_36m)
    st.write("")
    cols = st.columns(4)
    for col, (rotulo, chave) in zip(
        cols,
        [("12 meses", "preco_12m"), ("24 meses", "preco_24m"),
         ("48 meses", "preco_48m"), ("60 meses", "preco_60m")],
    ):
        with col:
            render_price_card(rotulo, format_brl(precos[chave]))


tab_precificacao, tab_reverso, tab_relatorio, tab_comprovacao = st.tabs(
    ["  Precificação  ", "  Cálculo Reverso  ", "  Relatório do Vendedor  ", "  Comprovação de Custo  "]
)


# =========================================================================== #
# ABA 1 — PRECIFICAÇÃO (multi-item)                                           #
# =========================================================================== #
with tab_precificacao:
    st.markdown("### Montar precificação")
    st.caption("Adicione um ou mais itens. O custo é privado e nunca sai no PDF.")

    st.markdown("#### Adicionar item")
    c1, c2 = st.columns([3, 1])
    with c1:
        add_desc = st.text_input(
            "Descrição do item", key="add_desc",
            placeholder="Ex.: Servidor HP ProLiant DL380 · 2x Xeon Silver · 64GB · 2x SSD 960GB",
        )
    with c2:
        add_qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="add_qtd")

    add_modo = st.radio(
        "Tipo de item",
        ["Por custo (calcula os prazos)", "Taxa fixa (mesmo valor em todos os prazos)"],
        key="add_modo", horizontal=True,
    )

    if add_modo.startswith("Por custo"):
        cc1, cc2 = st.columns(2)
        with cc1:
            add_custo = st.text_input("Custo unitário (R$) — privado", key="add_custo", placeholder="Ex.: 5.500,00")
        with cc2:
            add_coef = st.number_input(
                "Coeficiente 36 meses (%)", min_value=0.01, max_value=100.0,
                value=get_default_coef_pct(), step=0.1, format="%.2f", key="add_coef",
            )
    else:
        add_fixo = st.text_input("Valor mensal fixo por unidade (R$)", key="add_fixo", placeholder="Ex.: 78,00")

    add_evidencias = st.file_uploader(
        "Anexar comprovação do custo/preço (foto ou PDF) — necessário para gerar o PDF de Comprovação",
        type=["jpg", "jpeg", "png", "pdf"], accept_multiple_files=True, key="add_evidencias",
    )

    if st.button("➕ Adicionar item"):
        try:
            desc = (add_desc or "").strip()
            if not desc:
                raise ValueError("Informe a descrição do item.")
            if add_modo.startswith("Por custo"):
                custo = parse_brl_currency(add_custo)
                coef = add_coef / 100.0
                valores = calculate_prices_from_cost(custo, coef)
                item = {"descricao": desc, "quantidade": int(add_qtd), "fixo": False,
                        "custo": custo, "coef": coef, "valores": valores}
            else:
                v = parse_brl_currency(add_fixo)
                if v <= 0:
                    raise ValueError("O valor mensal fixo deve ser maior que zero.")
                valores = {k: round(v, 2) for k in TERMOS}
                item = {"descricao": desc, "quantidade": int(add_qtd), "fixo": True, "valores": valores}

            evidencias = []
            for f in (add_evidencias or []):
                ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else ""
                tipo = "imagem" if ext in ("jpg", "jpeg", "png") else "pdf"
                evidencias.append({"nome": f.name, "tipo": tipo, "bytes": f.getvalue()})
            item["evidencias"] = evidencias

            st.session_state["itens"].append(item)
            st.success("Item adicionado à proposta.")
        except ValueError as e:
            st.error(str(e))

    # ---- Proposta atual --------------------------------------------------- #
    itens = st.session_state["itens"]
    if itens:
        st.markdown("---")
        st.markdown("#### Proposta atual")
        totals = compute_totals(itens)
        render_items_table(itens, totals)

        st.write("")
        rc1, rc2, rc3 = st.columns([3, 1, 1])
        with rc1:
            idx = st.selectbox(
                "Selecione um item", options=list(range(len(itens))),
                format_func=lambda i: f"{i+1}. {itens[i]['descricao'][:60]}", key="rm_idx",
            )
        with rc2:
            st.write("")
            if st.button("Remover item"):
                itens.pop(idx)
                st.rerun()
        with rc3:
            st.write("")
            if st.button("Limpar tudo"):
                st.session_state["itens"] = []
                st.rerun()

        st.write("")
        responsavel = st.text_input(
            "Responsável / Assinatura", key="resp_main",
            value=st.session_state.get("responsavel", ""),
        )
        st.session_state["responsavel"] = responsavel
        render_note("Pronto. Abra a aba **Relatório do Vendedor** para gerar o PDF.", "info")
    else:
        render_note("Nenhum item adicionado ainda. Preencha acima e clique em **Adicionar item**.", "warn")


# =========================================================================== #
# ABA 2 — CÁLCULO REVERSO                                                     #
# =========================================================================== #
with tab_reverso:
    st.markdown("### Cálculo Reverso")
    st.caption("Descubra a base estimada a partir do preço de 36 meses.")
    render_note("Esta página é apenas para simulação interna — não gera PDF.", "warn")

    with st.form("form_reverso"):
        col1, col2 = st.columns(2)
        with col1:
            r_equip = st.text_input("Equipamento (opcional)", key="r_equip", placeholder="Descrição da máquina")
            r_preco36_in = st.text_input("Preço mensal de 36 meses (R$)", placeholder="Ex.: 195,00")
        with col2:
            r_coef_pct = st.number_input(
                "Coeficiente 36 meses (%)", min_value=0.01, max_value=100.0,
                value=get_default_coef_pct(), step=0.1, format="%.2f", key="r_coef",
            )
        r_submitted = st.form_submit_button("Calcular Base Estimada")

    if r_submitted:
        try:
            preco36 = parse_brl_currency(r_preco36_in)
            coef = r_coef_pct / 100.0
            base = calculate_cost_from_36m_price(preco36, coef)
            precos = calculate_prices_from_36m(preco36)

            st.markdown("---")
            st.markdown("#### Base estimada e simulação de prazos")
            c = st.columns([1, 1, 1])
            with c[1]:
                render_price_card("Base / custo estimado", format_brl(base), highlight=True, badge="Estimativa interna")
            st.write("")
            _render_price_grid(precos, badge_36m=None)

            st.write("")
            pct = f"{coef * 100:.2f}".rstrip("0").rstrip(".").replace(".", ",")
            render_note(
                f"<b>Fórmula:</b> custo estimado = preço 36m ÷ coeficiente = "
                f"{format_brl(preco36)} ÷ {pct}% = <b>{format_brl(base)}</b>", "info",
            )
            if r_equip:
                st.caption(f"Equipamento: {r_equip}")
        except ValueError as e:
            st.error(str(e))


# =========================================================================== #
# ABA 3 — RELATÓRIO DO VENDEDOR (PDF multi-item)                              #
# =========================================================================== #
with tab_relatorio:
    st.markdown("### Relatório do Vendedor")
    st.caption("PDF horizontal de consulta — preços de itens fora de portfólio.")
    render_note(
        "Uso interno. O PDF **não exibe** custo, coeficiente nem fórmula — só os preços "
        "que o vendedor pode usar com o cliente.", "info",
    )

    itens = st.session_state.get("itens", [])
    if not itens:
        render_note("Adicione itens na aba **Precificação** para liberar a geração do PDF.", "warn")
    else:
        totals = compute_totals(itens)
        responsavel = st.text_input(
            "Responsável / Assinatura", value=st.session_state.get("responsavel", ""), key="f_resp",
        )
        st.session_state["responsavel"] = responsavel
        data_emissao = datetime.now().strftime("%d/%m/%Y")

        st.markdown("---")
        st.markdown("#### Pré-visualização")
        st.markdown(
            f'<div style="background:{theme.PRIMARY_DARK};border-radius:12px 12px 0 0;'
            f'padding:16px 22px;border-bottom:3px solid {theme.ACCENT_COLOR}">'
            f'<div style="color:#fff;font-size:1.05rem;font-weight:800">Referência de Precificação de Locação</div>'
            f'<div style="color:#C7D2E5;font-size:.74rem;margin-top:3px;text-transform:uppercase;'
            f'letter-spacing:.06em">Uso interno · Consulta do vendedor</div>'
            f'<div style="color:#C7D2E5;font-size:.8rem;margin-top:4px">Emitido em: {data_emissao}</div></div>',
            unsafe_allow_html=True,
        )
        st.write("")
        render_items_table(itens, totals)

        st.write("")
        gen_col, dl_col = st.columns([1, 1])
        with gen_col:
            gerar = st.button("Gerar PDF")
        if gerar:
            try:
                report_data = {"itens": itens, "responsavel": responsavel, "data_emissao": data_emissao}
                base_desc = itens[0]["descricao"] if itens else "precificacao"
                slug = "".join(ch for ch in base_desc if ch.isalnum() or ch in " -_").strip().replace(" ", "_")[:40]
                filename = f"precificacao_{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                out_path = os.path.join(OUTPUT_DIR, filename)
                generate_executive_report(report_data, out_path)
                with open(out_path, "rb") as fh:
                    st.session_state["pdf_bytes"] = fh.read()
                st.session_state["pdf_name"] = filename
                st.success(f"PDF gerado: {filename}")
            except ValueError as e:
                st.error(str(e))

        if st.session_state.get("pdf_bytes"):
            with dl_col:
                st.download_button(
                    "Baixar PDF  ⬇",
                    data=st.session_state["pdf_bytes"],
                    file_name=st.session_state.get("pdf_name", "precificacao.pdf"),
                    mime="application/pdf",
                )


# =========================================================================== #
# ABA 4 — COMPROVAÇÃO DE CUSTO (memória de cálculo + evidência, uso interno)  #
# =========================================================================== #
with tab_comprovacao:
    st.markdown("### Comprovação de Custo")
    st.caption("Memória de cálculo e evidência de custo — documento interno para auditoria.")
    render_note(
        "Documento interno — uso restrito para auditoria e comprovação de custo. "
        "Nunca enviar a clientes ou fornecedores.", "warn",
    )

    itens = st.session_state.get("itens", [])
    if not itens:
        render_note("Adicione itens na aba **Precificação** para liberar esta área.", "warn")
    else:
        render_cost_proof_table(itens)

        faltando = [it["descricao"] for it in itens if not it.get("evidencias")]
        if faltando:
            render_note(
                "Itens sem evidência anexada: " + "; ".join(faltando) + ". "
                "Volte à aba Precificação e anexe a comprovação antes de gerar o PDF.", "warn",
            )

        st.write("")
        responsavel_cp = st.text_input(
            "Responsável / Assinatura", value=st.session_state.get("responsavel", ""), key="cp_resp",
        )
        st.session_state["responsavel"] = responsavel_cp

        st.write("")
        gen_col2, dl_col2 = st.columns([1, 1])
        with gen_col2:
            gerar_cp = st.button("Gerar PDF de Comprovação")
        if gerar_cp:
            try:
                base_desc = itens[0]["descricao"] if itens else "comprovacao"
                slug = "".join(ch for ch in base_desc if ch.isalnum() or ch in " -_").strip().replace(" ", "_")[:40]
                filename_cp = f"comprovacao_{slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                out_path_cp = os.path.join(OUTPUT_DIR, filename_cp)
                generate_cost_proof_report(itens, responsavel_cp, out_path_cp)
                with open(out_path_cp, "rb") as fh:
                    st.session_state["cp_pdf_bytes"] = fh.read()
                st.session_state["cp_pdf_name"] = filename_cp
                st.success(f"PDF de Comprovação gerado: {filename_cp}")
            except ValueError as e:
                st.error(str(e))

        if st.session_state.get("cp_pdf_bytes"):
            with dl_col2:
                st.download_button(
                    "Baixar PDF de Comprovação  ⬇",
                    data=st.session_state["cp_pdf_bytes"],
                    file_name=st.session_state.get("cp_pdf_name", "comprovacao.pdf"),
                    mime="application/pdf",
                    key="cp_download",
                )
