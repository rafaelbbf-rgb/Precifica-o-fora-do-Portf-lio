"""
report_generator.py
-------------------
Gera o PDF interno de precificação (consulta do vendedor) em formato HORIZONTAL
(paisagem), com a identidade Office Total. Suporta múltiplos itens, linha de
total e itens de "taxa fixa" (mesmo valor em todos os prazos).

O PDF NUNCA exibe custo, coeficiente, margem ou fórmula.
"""

import os
from datetime import datetime
from typing import Dict, List

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
)

from . import theme
from .formatting import format_brl

# --------------------------------------------------------------------------- #
# Layout (A4 paisagem)                                                        #
# --------------------------------------------------------------------------- #
PAGE_W, PAGE_H = landscape(A4)      # ~841.9 x 595.3 pt
BAND_H = 28 * mm
MARGIN_X = 16 * mm

_PRIMARY = HexColor(theme.PRIMARY_COLOR)
_PRIMARY_DARK = HexColor(theme.PRIMARY_DARK)
_ACCENT = HexColor(theme.ACCENT_COLOR)
_BORDER = HexColor(theme.BORDER_COLOR)
_TEXT = HexColor(theme.TEXT_COLOR)
_MUTED = HexColor(theme.MUTED_TEXT_COLOR)
_COL36 = HexColor("#EEF3FA")
_ZEBRA = HexColor("#FAFBFC")
_FIXED_BG = HexColor("#E9F8EF")
_FIXED_TX = HexColor("#1F8A57")

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

_TERMS = [
    ("12 meses", "preco_12m"),
    ("24 meses", "preco_24m"),
    ("36 meses", "preco_36m"),
    ("48 meses", "preco_48m"),
    ("60 meses", "preco_60m"),
]


def _styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "section": ParagraphStyle("section", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=8.5, textColor=_MUTED, spaceAfter=4, leading=11, alignment=TA_LEFT),
        "cell_l": ParagraphStyle("cell_l", parent=base["Normal"], fontName="Helvetica",
                                 fontSize=9.5, textColor=_TEXT, leading=13, alignment=TA_LEFT),
        "cell_lb": ParagraphStyle("cell_lb", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=9.5, textColor=_TEXT, leading=13, alignment=TA_LEFT),
        "head": ParagraphStyle("head", parent=base["Normal"], fontName="Helvetica-Bold",
                               fontSize=8, textColor=white, leading=11, alignment=TA_RIGHT),
        "head_l": ParagraphStyle("head_l", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=8, textColor=white, leading=11, alignment=TA_LEFT),
        "num": ParagraphStyle("num", parent=base["Normal"], fontName="Helvetica",
                              fontSize=9.5, textColor=_TEXT, leading=13, alignment=TA_RIGHT),
        "num36": ParagraphStyle("num36", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=9.5, textColor=_PRIMARY, leading=13, alignment=TA_RIGHT),
        "qty": ParagraphStyle("qty", parent=base["Normal"], fontName="Helvetica",
                              fontSize=9.5, textColor=_TEXT, leading=13, alignment=TA_CENTER),
        "fixed": ParagraphStyle("fixed", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=9.5, textColor=_FIXED_TX, leading=13, alignment=TA_CENTER),
        "tot_l": ParagraphStyle("tot_l", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=10, textColor=white, leading=13, alignment=TA_LEFT),
        "tot_n": ParagraphStyle("tot_n", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=10, textColor=white, leading=13, alignment=TA_RIGHT),
        "sign_name": ParagraphStyle("sign_name", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=10, textColor=_TEXT, leading=13),
        "sign_org": ParagraphStyle("sign_org", parent=base["Normal"], fontName="Helvetica",
                                   fontSize=8.5, textColor=_MUTED, leading=11),
    }


# --------------------------------------------------------------------------- #
# Faixa e rodapé                                                              #
# --------------------------------------------------------------------------- #
def _draw_header_footer(canvas, doc):
    canvas.saveState()

    canvas.setFillColor(_PRIMARY_DARK)
    canvas.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, fill=1, stroke=0)
    canvas.setFillColor(_ACCENT)
    canvas.rect(0, PAGE_H - BAND_H, PAGE_W, 1.5 * mm, fill=1, stroke=0)

    logo = os.path.join(_ASSETS, "logo_white.png")
    if os.path.exists(logo):
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(logo)
            iw, ih = img.getSize()
            th = 8 * mm
            tw = th * (iw / ih)
            canvas.drawImage(img, MARGIN_X, PAGE_H - 13 * mm, width=tw, height=th,
                             mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    canvas.setFillColor(white)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(MARGIN_X, PAGE_H - 20 * mm, "Referência de Precificação de Locação")

    data_emissao = getattr(doc, "_data_emissao", datetime.now().strftime("%d/%m/%Y"))
    canvas.setFont("Helvetica", 8.5)
    canvas.setFillColor(HexColor("#C7D2E5"))
    canvas.drawString(MARGIN_X, PAGE_H - 24.5 * mm, f"Emitido em: {data_emissao}")

    badge_txt = "USO INTERNO · CONSULTA DO VENDEDOR"
    canvas.setFont("Helvetica-Bold", 7)
    bw = canvas.stringWidth(badge_txt, "Helvetica-Bold", 7) + 16
    bx = PAGE_W - MARGIN_X - bw
    by = PAGE_H - 13 * mm
    canvas.setFillColor(_ACCENT)
    canvas.roundRect(bx, by, bw, 6 * mm, 3, fill=1, stroke=0)
    canvas.setFillColor(_PRIMARY_DARK)
    canvas.drawCentredString(bx + bw / 2, by + 2 * mm, badge_txt)

    canvas.setStrokeColor(_BORDER)
    canvas.setLineWidth(0.6)
    canvas.line(MARGIN_X, 13 * mm, PAGE_W - MARGIN_X, 13 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(_MUTED)
    canvas.drawCentredString(PAGE_W / 2, 9 * mm,
                             "Documento de uso interno da equipe comercial. "
                             "Valores sujeitos à validação, disponibilidade e condições comerciais vigentes.")
    canvas.setFillColor(_PRIMARY)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.drawCentredString(PAGE_W / 2, 6 * mm, "Grupo Office Total · Tecnologia por Assinatura")

    canvas.restoreState()


# --------------------------------------------------------------------------- #
# Cálculo de totais                                                           #
# --------------------------------------------------------------------------- #
def compute_totals(itens: List[Dict]) -> Dict[str, float]:
    totals = {chave: 0.0 for _, chave in _TERMS}
    for it in itens:
        q = it.get("quantidade", 1)
        for _, chave in _TERMS:
            totals[chave] += it["valores"][chave] * q
    return {k: round(v, 2) for k, v in totals.items()}


# --------------------------------------------------------------------------- #
# Tabela horizontal                                                           #
# --------------------------------------------------------------------------- #
def _items_table(itens: List[Dict], totals: Dict, st: Dict) -> Table:
    content_w = PAGE_W - 2 * MARGIN_X
    qty_w = 18 * mm
    term_w = 32 * mm
    desc_w = content_w - qty_w - 5 * term_w

    col_widths = [desc_w, qty_w] + [term_w] * 5

    header = [Paragraph("Descrição", st["head_l"]), Paragraph("Qtd", st["head"])]
    header += [Paragraph(rotulo, st["head"]) for rotulo, _ in _TERMS]
    rows = [header]

    spans = []          # SPAN commands for fixed-fee rows
    fixed_rows = []
    for r, it in enumerate(itens, start=1):
        q = it.get("quantidade", 1)
        desc = it.get("descricao") or "—"
        if it.get("fixo"):
            val = format_brl(it["valores"]["preco_36m"] * q)
            row = [Paragraph(desc, st["cell_l"]), Paragraph(str(q), st["qty"]),
                   Paragraph(f"{val} · taxa fixa", st["fixed"]), "", "", "", ""]
            spans.append(("SPAN", (2, r), (6, r)))
            fixed_rows.append(r)
        else:
            row = [Paragraph(desc, st["cell_l"]), Paragraph(str(q), st["qty"])]
            for _, chave in _TERMS:
                sty = st["num36"] if chave == "preco_36m" else st["num"]
                row.append(Paragraph(format_brl(it["valores"][chave] * q), sty))
        rows.append(row)

    total_row = [Paragraph("Total mensal", st["tot_l"]), ""]
    total_row += [Paragraph(format_brl(totals[chave]), st["tot_n"]) for _, chave in _TERMS]
    rows.append(total_row)
    total_idx = len(rows) - 1

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, _BORDER),
        ("BOX", (0, 0), (-1, -1), 0.6, _BORDER),
        ("LINEAFTER", (0, 0), (-2, -1), 0.4, _BORDER),
        # coluna 36 meses destacada (índice 4) nas linhas de itens
        ("BACKGROUND", (4, 1), (4, total_idx - 1), _COL36),
        # linha de total
        ("BACKGROUND", (0, total_idx), (-1, total_idx), _PRIMARY_DARK),
        ("LINEABOVE", (0, total_idx), (-1, total_idx), 1.2, _ACCENT),
    ]
    # zebra nas linhas de itens (linhas pares)
    for r in range(1, total_idx):
        if r % 2 == 0 and r not in fixed_rows:
            style.append(("BACKGROUND", (0, r), (3, r), _ZEBRA))
            style.append(("BACKGROUND", (5, r), (-1, r), _ZEBRA))
    # células de taxa fixa
    for r in fixed_rows:
        style.append(("BACKGROUND", (2, r), (6, r), _FIXED_BG))
    style += spans
    t.setStyle(TableStyle(style))
    return t


# --------------------------------------------------------------------------- #
# Função principal                                                            #
# --------------------------------------------------------------------------- #
def generate_executive_report(data: Dict, output_path: str) -> str:
    """
    Gera o PDF horizontal (paisagem) de precificação com um ou mais itens.

    Chaves esperadas em `data`:
        itens         (list de dicts: descricao, quantidade, fixo, valores{preco_*})
        responsavel   (str)
        data_emissao  (str, opcional — padrão = hoje)

    Levanta ValueError se não houver itens válidos.
    """
    itens = data.get("itens") or []
    if not itens:
        raise ValueError("Adicione ao menos um item antes de gerar o PDF.")
    for it in itens:
        if not it.get("valores", {}).get("preco_36m"):
            raise ValueError("Há item sem preço calculado. Recalcule a precificação.")

    totals = compute_totals(itens)
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    st = _styles()

    doc = BaseDocTemplate(
        output_path, pagesize=landscape(A4),
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=BAND_H + 6 * mm, bottomMargin=16 * mm,
        title="Referência de Precificação de Locação", author="Grupo Office Total",
    )
    doc._data_emissao = data.get("data_emissao") or datetime.now().strftime("%d/%m/%Y")

    frame = Frame(MARGIN_X, 16 * mm, PAGE_W - 2 * MARGIN_X,
                  PAGE_H - BAND_H - 6 * mm - 16 * mm,
                  id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_draw_header_footer)])

    story = [
        Paragraph("LOCAÇÃO MENSAL POR PRAZO", st["section"]),
        Spacer(1, 4),
        _items_table(itens, totals, st),
        Spacer(1, 30),
    ]

    responsavel = (data.get("responsavel") or "").strip() or "Responsável Comercial"
    sign = Table(
        [[Paragraph("_______________________________________", st["sign_org"])],
         [Paragraph(responsavel, st["sign_name"])],
         [Paragraph("Grupo Office Total", st["sign_org"])]],
        colWidths=[80 * mm],
    )
    sign.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(sign)

    doc.build(story)
    return output_path
