"""
theme.py
--------
Design system da Office Total: tokens de cor e injeção de CSS customizado
no Streamlit para dar à interface aparência de produto interno premium.

Todas as cores foram extraídas dos arquivos oficiais da marca (papel timbrado
.docx e template .pptx). Para reposicionar a identidade, altere apenas as
constantes abaixo.
"""

# --------------------------------------------------------------------------- #
# Tokens de cor (design system)                                               #
# --------------------------------------------------------------------------- #
PRIMARY_COLOR = "#19396A"      # marinho institucional (logo)
PRIMARY_DARK = "#002060"       # marinho profundo (faixas / cabeçalhos)
SECONDARY_COLOR = "#007DAA"    # azul-petróleo de apoio
ACCENT_COLOR = "#12ABC2"       # ciano (destaques, hover, detalhes)
ACCENT_BRIGHT = "#00B4C3"      # ciano vivo (realces pontuais)
BACKGROUND_COLOR = "#F5F7FA"   # fundo geral, frio e leve
CARD_BACKGROUND = "#FFFFFF"    # cards
BORDER_COLOR = "#E2E8F0"       # bordas sutis
TEXT_COLOR = "#1A2333"         # texto principal
MUTED_TEXT_COLOR = "#6B7280"   # texto secundário
SUCCESS_COLOR = "#2BA872"      # sucesso
WARNING_COLOR = "#E8A33D"      # alerta / aviso


def apply_office_total_theme() -> None:
    """Injeta o CSS customizado da Office Total no app Streamlit."""
    import streamlit as st

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {{
        --ot-primary: {PRIMARY_COLOR};
        --ot-primary-dark: {PRIMARY_DARK};
        --ot-secondary: {SECONDARY_COLOR};
        --ot-accent: {ACCENT_COLOR};
        --ot-accent-bright: {ACCENT_BRIGHT};
        --ot-bg: {BACKGROUND_COLOR};
        --ot-card: {CARD_BACKGROUND};
        --ot-border: {BORDER_COLOR};
        --ot-text: {TEXT_COLOR};
        --ot-muted: {MUTED_TEXT_COLOR};
        --ot-success: {SUCCESS_COLOR};
        --ot-warning: {WARNING_COLOR};
    }}

    /* Base ------------------------------------------------------------ */
    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}
    .stApp {{
        background: var(--ot-bg);
        color: var(--ot-text);
    }}
    /* Esconde o chrome padrão do Streamlit */
    #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; height: 0; }}
    .block-container {{ padding-top: 1.5rem; max-width: 1180px; }}

    /* Tipografia ------------------------------------------------------ */
    h1, h2, h3, h4 {{ color: var(--ot-primary); font-weight: 700; letter-spacing: -0.01em; }}

    /* Cabeçalho institucional ---------------------------------------- */
    .ot-header {{
        display: flex; align-items: center; justify-content: space-between;
        background: var(--ot-card);
        border: 1px solid var(--ot-border);
        border-top: 4px solid var(--ot-primary);
        border-radius: 14px;
        padding: 18px 26px;
        margin-bottom: 8px;
        box-shadow: 0 4px 18px rgba(25,57,106,0.06);
    }}
    .ot-header .ot-title {{ font-size: 1.25rem; font-weight: 800; color: var(--ot-primary); margin: 0; }}
    .ot-header .ot-subtitle {{ font-size: 0.85rem; color: var(--ot-muted); margin: 2px 0 0; }}
    .ot-header img {{ height: 40px; }}

    /* Cards de preço -------------------------------------------------- */
    .ot-card {{
        background: var(--ot-card);
        border: 1px solid var(--ot-border);
        border-radius: 14px;
        padding: 20px 22px;
        box-shadow: 0 4px 16px rgba(25,57,106,0.05);
        height: 100%;
    }}
    .ot-price-card {{
        background: var(--ot-card);
        border: 1px solid var(--ot-border);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(25,57,106,0.05);
        transition: transform .15s ease, box-shadow .15s ease;
    }}
    .ot-price-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 22px rgba(25,57,106,0.10); }}
    .ot-price-card .ot-term {{ font-size: 0.78rem; font-weight: 600; color: var(--ot-muted);
        text-transform: uppercase; letter-spacing: 0.06em; }}
    .ot-price-card .ot-value {{ font-size: 1.55rem; font-weight: 800; color: var(--ot-primary); margin-top: 4px; }}
    .ot-price-card .ot-bar {{ height: 3px; width: 34px; background: var(--ot-accent);
        border-radius: 3px; margin: 10px auto 0; }}

    /* Card de destaque (36 meses) */
    .ot-price-card.highlight {{
        background: linear-gradient(135deg, {PRIMARY_COLOR} 0%, {PRIMARY_DARK} 100%);
        border: none;
        box-shadow: 0 10px 28px rgba(0,32,96,0.28);
    }}
    .ot-price-card.highlight .ot-term {{ color: rgba(255,255,255,0.75); }}
    .ot-price-card.highlight .ot-value {{ color: #FFFFFF; font-size: 2.1rem; }}
    .ot-price-card.highlight .ot-bar {{ background: var(--ot-accent-bright); }}
    .ot-badge {{ display: inline-block; background: rgba(255,255,255,0.16); color: #fff;
        font-size: 0.66rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase;
        padding: 3px 10px; border-radius: 999px; margin-bottom: 8px; }}

    /* Card de preço de venda */
    .ot-sale-card {{
        background: #ECFAFD; border: 1px solid #BDEAF1; border-left: 4px solid var(--ot-accent);
        border-radius: 12px; padding: 16px 20px;
    }}
    .ot-sale-card .ot-term {{ font-size: 0.78rem; font-weight: 600; color: var(--ot-secondary);
        text-transform: uppercase; letter-spacing: 0.05em; }}
    .ot-sale-card .ot-value {{ font-size: 1.5rem; font-weight: 800; color: var(--ot-secondary); }}

    /* Resumo do equipamento */
    .ot-summary {{ background: var(--ot-card); border: 1px solid var(--ot-border);
        border-radius: 14px; padding: 20px 24px; box-shadow: 0 4px 16px rgba(25,57,106,0.05); }}
    .ot-summary h4 {{ margin: 0 0 12px; font-size: 0.8rem; text-transform: uppercase;
        letter-spacing: 0.08em; color: var(--ot-muted); }}
    .ot-summary .ot-row {{ display: flex; padding: 7px 0; border-bottom: 1px solid var(--ot-border); }}
    .ot-summary .ot-row:last-child {{ border-bottom: none; }}
    .ot-summary .ot-key {{ width: 150px; min-width: 150px; color: var(--ot-muted); font-size: 0.9rem; }}
    .ot-summary .ot-val {{ color: var(--ot-text); font-size: 0.95rem; font-weight: 500; }}

    /* Avisos ---------------------------------------------------------- */
    .ot-note {{ border-radius: 12px; padding: 12px 18px; font-size: 0.88rem; margin: 4px 0 14px;
        display: flex; gap: 8px; align-items: center; }}
    .ot-note.info {{ background: #ECFAFD; border: 1px solid #BDEAF1; color: var(--ot-secondary); }}
    .ot-note.warn {{ background: #FFF6E9; border: 1px solid #F4DDB4; color: #9A6A14; }}

    /* Botões ---------------------------------------------------------- */
    .stButton > button, .stDownloadButton > button {{
        background: var(--ot-primary); color: #fff; border: none; border-radius: 8px;
        padding: 0.55rem 1.3rem; font-weight: 600; font-size: 0.95rem;
        box-shadow: 0 4px 12px rgba(25,57,106,0.18); transition: background .15s ease, transform .1s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: var(--ot-accent); color: #fff; transform: translateY(-1px);
    }}
    .stButton > button:focus {{ box-shadow: 0 0 0 3px rgba(18,171,194,0.35); }}

    /* Inputs ---------------------------------------------------------- */
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {{
        border-radius: 8px !important; border: 1px solid var(--ot-border) !important;
        background: #fff !important;
    }}
    [data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus,
    [data-testid="stTextArea"] textarea:focus {{
        border-color: var(--ot-accent) !important; box-shadow: 0 0 0 2px rgba(18,171,194,0.18) !important;
    }}
    label, .stMarkdown p {{ color: var(--ot-text); }}

    /* Abas ------------------------------------------------------------ */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid var(--ot-border); }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent; border-radius: 8px 8px 0 0; padding: 10px 20px;
        font-weight: 600; color: var(--ot-muted);
    }}
    .stTabs [aria-selected="true"] {{ color: var(--ot-primary); border-bottom: 3px solid var(--ot-accent); }}

    /* Tabela de itens (proposta) ------------------------------------- */
    .ot-table {{ width:100%; border-collapse:collapse; background:var(--ot-card);
        border:1px solid var(--ot-border); border-radius:12px; overflow:hidden; font-size:0.88rem; }}
    .ot-table thead th {{ background:var(--ot-primary); color:#fff; font-weight:600; font-size:0.72rem;
        text-transform:uppercase; letter-spacing:0.04em; padding:11px 12px; text-align:right; white-space:nowrap; }}
    .ot-table thead th.left {{ text-align:left; }}
    .ot-table tbody td {{ padding:11px 12px; border-top:1px solid var(--ot-border);
        text-align:right; color:var(--ot-text); white-space:nowrap; }}
    .ot-table tbody td.left {{ text-align:left; white-space:normal; }}
    .ot-table tbody tr:nth-child(even) td {{ background:#FAFBFC; }}
    .ot-table tbody td.col36 {{ background:#EEF3FA; font-weight:700; color:var(--ot-primary); }}
    .ot-table tbody tr.fixed td.fixedval {{ background:#E9F8EF; color:#1F8A57; font-weight:600; text-align:center; }}
    .ot-table tbody tr.total td {{ background:var(--ot-primary-dark); color:#fff; font-weight:700;
        border-top:2px solid var(--ot-accent); }}

    /* Divisores */
    hr {{ border-color: var(--ot-border); }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
