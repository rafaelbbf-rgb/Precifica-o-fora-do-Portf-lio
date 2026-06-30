"""
cost_proof_generator.py
------------------------
Gera o PDF interno de "Memória de Cálculo e Comprovação de Custo" —
documento CONFIDENCIAL, separado do Relatório do Vendedor, usado para
auditoria e comprovação de como o custo e o coeficiente de cada item
foram definidos.

Combina, num único PDF:
  1. a memória de cálculo (custo, coeficiente, preços) de todos os itens;
  2. a evidência anexada de cada item — imagens incorporadas como página,
     PDFs mesclados como páginas adicionais.

Este módulo NUNCA é usado pelo fluxo do vendedor. `report_generator.py`
(Relatório do Vendedor) permanece absolutamente intocado.
"""

import io
import os
from datetime import datetime
from typing import Dict, List

from pypdf import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
)

from . import theme
from .formatting import format_brl
from .report_generator import compute_totals

# --------------------------------------------------------------------------- #
# Layout                                                                       #
# --------------------------------------------------------------------------- #
PAGE_W, PAGE_H = landscape(A4)        # páginas de memória de cálculo
PORTRAIT_W, PORTRAIT_H = A4           # páginas de evidência
BAND_H = 28 * mm
MARGIN_X = 16 * mm

_PRIMARY = HexColor(theme.PRIMARY_COLOR)
_PRIMARY_DARK = HexColor(theme.PRIMARY_DARK)
_WARNING = HexColor(theme.WARNING_COLOR)
_BORDER = HexColor(theme.BORDER_COLOR)
_TEXT = HexColor(theme.TEXT_COLOR)
_MUTED = HexColor(theme.MUTED_TEXT_COLOR)
_ZEBRA = HexColor("#FAFBFC")
_FIXED_BG = HexColor("#E9F8EF")
_FIXED_TX = HexColor("#1F8A57")
_ALERT_TEXT = HexColor("#B5391E")

_ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

_TERMS = [
    ("12 meses", "preco_12m"),
    ("24 meses", "preco_24m"),
    ("36 meses", "preco_36m"),
    ("48 meses", "preco_48m"),
    ("60 meses", "preco_60m"),
]


def _truncate_to_width(c, text: str, font: str, size: float, max_width: float) -> str:
    """Trunca `text` com reticências se ultrapassar `max_width` na fonte/tamanho dados."""
    if c.stringWidth(text, font, size) <= max_width:
        return text
    ellipsis = "…"
    while text and c.stringWidth(text + ellipsis, font, size) > max_width:
        text = text[:-1]
    return text + ellipsis


def _styles() -> Dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "section": ParagraphStyle("section", parent=base["Normal"], fontName="Helvetica-Bold",
                                  fontSize=8.5, textColor=_MUTED, spaceAfter=4, leading=11, alignment=TA_LEFT),
        "cell_l": ParagraphStyle("cell_l", parent=base["Normal"], fontName="Helvetica",
                                 fontSize=8.5, textColor=_TEXT, leading=11, alignment=TA_LEFT),
        "head": ParagraphStyle("head", parent=base["Normal"], fontName="Helvetica-Bold",
                               fontSize=7.5, textColor=white, leading=10, alignment=TA_RIGHT),
        "head_l": ParagraphStyle("head_l", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=7.5, textColor=white, leading=10, alignment=TA_LEFT),
        "num": ParagraphStyle("num", parent=base["Normal"], fontName="Helvetica",
                              fontSize=8.5, textColor=_TEXT, leading=11, alignment=TA_RIGHT),
        "num36": ParagraphStyle("num36", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=8.5, textColor=_PRIMARY, leading=11, alignment=TA_RIGHT),
        "qty": ParagraphStyle("qty", parent=base["Normal"], fontName="Helvetica",
                              fontSize=8.5, textColor=_TEXT, leading=11, alignment=TA_CENTER),
        "fixed": ParagraphStyle("fixed", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=8, textColor=_FIXED_TX, leading=11, alignment=TA_CENTER),
        "tot_l": ParagraphStyle("tot_l", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=9.5, textColor=white, leading=12, alignment=TA_LEFT),
        "tot_n": ParagraphStyle("tot_n", parent=base["Normal"], fontName="Helvetica-Bold",
                                fontSize=9.5, textColor=white, leading=12, alignment=TA_RIGHT),
        "sign_name": ParagraphStyle("sign_name", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=10, textColor=_TEXT, leading=13),
        "sign_org": ParagraphStyle("sign_org", parent=base["Normal"], fontName="Helvetica",
                                   fontSize=8.5, textColor=_MUTED, leading=11),
    }


# --------------------------------------------------------------------------- #
# Faixa e rodapé (seção de memória, paisagem)                                 #
# --------------------------------------------------------------------------- #
def _draw_header_footer(canvas_obj, doc):
    canvas_obj.saveState()

    canvas_obj.setFillColor(_PRIMARY_DARK)
    canvas_obj.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, fill=1, stroke=0)
    canvas_obj.setFillColor(_WARNING)
    canvas_obj.rect(0, PAGE_H - BAND_H, PAGE_W, 1.5 * mm, fill=1, stroke=0)

    logo = os.path.join(_ASSETS, "logo_white.png")
    if os.path.exists(logo):
        try:
            img = ImageReader(logo)
            iw, ih = img.getSize()
            th = 8 * mm
            tw = th * (iw / ih)
            canvas_obj.drawImage(img, MARGIN_X, PAGE_H - 13 * mm, width=tw, height=th,
                                  mask="auto", preserveAspectRatio=True)
        except Exception:
            pass

    canvas_obj.setFillColor(white)
    canvas_obj.setFont("Helvetica-Bold", 14)
    canvas_obj.drawString(MARGIN_X, PAGE_H - 20 * mm, "Memória de Cálculo e Comprovação de Custo")

    data_emissao = getattr(doc, "_data_emissao", datetime.now().strftime("%d/%m/%Y"))
    responsavel = getattr(doc, "_responsavel", "") or ""
    sub = f"Emitido em: {data_emissao}"
    if responsavel:
        sub += f"   ·   Responsável: {responsavel}"
    canvas_obj.setFont("Helvetica", 8.5)
    canvas_obj.setFillColor(HexColor("#C7D2E5"))
    sub = _truncate_to_width(canvas_obj, sub, "Helvetica", 8.5, PAGE_W - 2 * MARGIN_X)
    canvas_obj.drawString(MARGIN_X, PAGE_H - 24.5 * mm, sub)

    badge_txt = "CONFIDENCIAL · USO INTERNO · COMPROVAÇÃO DE CUSTO"
    canvas_obj.setFont("Helvetica-Bold", 7)
    bw = canvas_obj.stringWidth(badge_txt, "Helvetica-Bold", 7) + 16
    bx = PAGE_W - MARGIN_X - bw
    by = PAGE_H - 13 * mm
    canvas_obj.setFillColor(_WARNING)
    canvas_obj.roundRect(bx, by, bw, 6 * mm, 3, fill=1, stroke=0)
    canvas_obj.setFillColor(_PRIMARY_DARK)
    canvas_obj.drawCentredString(bx + bw / 2, by + 2 * mm, badge_txt)

    canvas_obj.setStrokeColor(_BORDER)
    canvas_obj.setLineWidth(0.6)
    canvas_obj.line(MARGIN_X, 13 * mm, PAGE_W - MARGIN_X, 13 * mm)
    canvas_obj.setFont("Helvetica-Bold", 7.5)
    canvas_obj.setFillColor(_ALERT_TEXT)
    canvas_obj.drawCentredString(
        PAGE_W / 2, 9 * mm,
        "Documento interno destinado a auditoria e comprovação de custo. "
        "NÃO compartilhar com clientes ou fornecedores.",
    )
    canvas_obj.setFillColor(_PRIMARY)
    canvas_obj.setFont("Helvetica-Bold", 7.5)
    canvas_obj.drawCentredString(PAGE_W / 2, 6 * mm, "Grupo Office Total · Tecnologia por Assinatura")

    canvas_obj.restoreState()


# --------------------------------------------------------------------------- #
# Tabela de memória de cálculo (custo + coeficiente expostos de propósito)    #
# --------------------------------------------------------------------------- #
def _memory_table(itens: List[Dict], totals: Dict, st: Dict) -> Table:
    content_w = PAGE_W - 2 * MARGIN_X
    desc_w = 64 * mm
    qty_w = 12 * mm
    custo_w = 26 * mm
    coef_w = 22 * mm
    term_w = (content_w - desc_w - qty_w - custo_w - coef_w) / 5

    col_widths = [desc_w, qty_w, custo_w, coef_w] + [term_w] * 5

    header = [
        Paragraph("Descrição", st["head_l"]), Paragraph("Qtd", st["head"]),
        Paragraph("Custo unit.", st["head"]), Paragraph("Coeficiente", st["head"]),
    ]
    header += [Paragraph(rotulo, st["head"]) for rotulo, _ in _TERMS]
    rows = [header]

    fixed_rows = []
    for r, it in enumerate(itens, start=1):
        q = it.get("quantidade", 1)
        desc = it.get("descricao") or "—"
        if it.get("fixo"):
            fixed_rows.append(r)
            row = [Paragraph(desc, st["cell_l"]), Paragraph(str(q), st["qty"]),
                   Paragraph("—", st["qty"]), Paragraph("taxa fixa", st["fixed"])]
            for _, chave in _TERMS:
                row.append(Paragraph(format_brl(it["valores"][chave] * q), st["num"]))
        else:
            custo = it.get("custo", 0)
            coef = it.get("coef", 0)
            coef_str = f"{coef * 100:.2f}".rstrip("0").rstrip(".").replace(".", ",") + "%"
            row = [Paragraph(desc, st["cell_l"]), Paragraph(str(q), st["qty"]),
                   Paragraph(format_brl(custo), st["num"]), Paragraph(coef_str, st["num"])]
            for _, chave in _TERMS:
                sty = st["num36"] if chave == "preco_36m" else st["num"]
                row.append(Paragraph(format_brl(it["valores"][chave] * q), sty))
        rows.append(row)

    total_row = [Paragraph("Total mensal", st["tot_l"]), "", "", ""]
    total_row += [Paragraph(format_brl(totals[chave]), st["tot_n"]) for _, chave in _TERMS]
    rows.append(total_row)
    total_idx = len(rows) - 1

    t = Table(rows, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), _PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, _BORDER),
        ("BOX", (0, 0), (-1, -1), 0.6, _BORDER),
        ("BACKGROUND", (0, total_idx), (-1, total_idx), _PRIMARY_DARK),
        ("LINEABOVE", (0, total_idx), (-1, total_idx), 1.2, _WARNING),
    ]
    for r in range(1, total_idx):
        if r % 2 == 0:
            style.append(("BACKGROUND", (0, r), (-1, r), _ZEBRA))
    for r in fixed_rows:
        style.append(("BACKGROUND", (2, r), (3, r), _FIXED_BG))
    t.setStyle(TableStyle(style))
    return t


def _build_memory_pdf_bytes(itens: List[Dict], responsavel: str, data_emissao: str) -> bytes:
    """Gera as páginas de memória de cálculo (paisagem) como bytes de PDF."""
    totals = compute_totals(itens)
    st_styles = _styles()
    buf = io.BytesIO()

    doc = BaseDocTemplate(
        buf, pagesize=landscape(A4),
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=BAND_H + 6 * mm, bottomMargin=16 * mm,
        title="Memória de Cálculo e Comprovação de Custo", author="Grupo Office Total",
    )
    doc._data_emissao = data_emissao
    doc._responsavel = responsavel

    frame = Frame(MARGIN_X, 16 * mm, PAGE_W - 2 * MARGIN_X,
                  PAGE_H - BAND_H - 6 * mm - 16 * mm,
                  id="body", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_draw_header_footer)])

    story = [
        Paragraph("MEMÓRIA DE CÁLCULO — CUSTO, COEFICIENTE E PREÇOS APLICADOS", st_styles["section"]),
        Spacer(1, 4),
        _memory_table(itens, totals, st_styles),
        Spacer(1, 24),
    ]

    sign = Table(
        [[Paragraph("_______________________________________", st_styles["sign_org"])],
         [Paragraph(responsavel or "Responsável Comercial", st_styles["sign_name"])],
         [Paragraph("Grupo Office Total", st_styles["sign_org"])]],
        colWidths=[80 * mm],
    )
    sign.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    story.append(sign)

    doc.build(story)
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# Páginas de evidência (retrato)                                              #
# --------------------------------------------------------------------------- #
def _build_image_evidence_page_bytes(item_desc: str, evid_nome: str, img_bytes: bytes) -> bytes:
    """Página A4 retrato com cabeçalho + a imagem de evidência incorporada."""
    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=A4)
    c.setFillColor(_PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    titulo = _truncate_to_width(c, f"Evidência — {item_desc}", "Helvetica-Bold", 12, PORTRAIT_W - 2 * MARGIN_X)
    c.drawString(MARGIN_X, PORTRAIT_H - 18 * mm, titulo)
    c.setFillColor(_MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN_X, PORTRAIT_H - 23 * mm, f"Arquivo: {evid_nome}")
    c.setStrokeColor(_BORDER)
    c.line(MARGIN_X, PORTRAIT_H - 26 * mm, PORTRAIT_W - MARGIN_X, PORTRAIT_H - 26 * mm)

    try:
        img = ImageReader(io.BytesIO(img_bytes))
        iw, ih = img.getSize()
        max_w = PORTRAIT_W - 2 * MARGIN_X
        max_h = PORTRAIT_H - 40 * mm
        scale = min(max_w / iw, max_h / ih)
        draw_w, draw_h = iw * scale, ih * scale
        x = (PORTRAIT_W - draw_w) / 2
        y = (PORTRAIT_H - 30 * mm - draw_h) / 2 + 4 * mm
        c.drawImage(img, x, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")
    except Exception:
        c.setFillColor(_MUTED)
        c.setFont("Helvetica", 9)
        c.drawString(MARGIN_X, PORTRAIT_H / 2, "Não foi possível exibir esta imagem.")

    c.showPage()
    c.save()
    return buf.getvalue()


def _build_pdf_evidence_header_bytes(item_desc: str, evid_nome: str) -> bytes:
    """Página de cabeçalho (retrato) inserida antes de um PDF de evidência mesclado."""
    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=A4)
    c.setFillColor(_PRIMARY)
    c.setFont("Helvetica-Bold", 12)
    titulo = _truncate_to_width(c, f"Evidência — {item_desc}", "Helvetica-Bold", 12, PORTRAIT_W - 2 * MARGIN_X)
    c.drawString(MARGIN_X, PORTRAIT_H - 18 * mm, titulo)
    c.setFillColor(_MUTED)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN_X, PORTRAIT_H - 23 * mm, f"Arquivo anexado: {evid_nome} (páginas a seguir)")
    c.setStrokeColor(_BORDER)
    c.line(MARGIN_X, PORTRAIT_H - 26 * mm, PORTRAIT_W - MARGIN_X, PORTRAIT_H - 26 * mm)
    c.showPage()
    c.save()
    return buf.getvalue()


# --------------------------------------------------------------------------- #
# Função principal                                                            #
# --------------------------------------------------------------------------- #
def generate_cost_proof_report(itens: List[Dict], responsavel: str, output_path: str) -> str:
    """
    Gera o PDF interno de Memória de Cálculo e Comprovação de Custo, combinando:
      - tabela de memória de cálculo (custo, coeficiente, preços) de todos os itens;
      - a evidência anexada de cada item (imagens incorporadas; PDFs mesclados).

    Levanta ValueError se não houver itens, ou se algum item não tiver
    evidência anexada (a comprovação exige evidência para TODOS os itens).
    """
    if not itens:
        raise ValueError("Adicione ao menos um item antes de gerar o PDF de Comprovação.")

    sem_evidencia = [it.get("descricao", "item") for it in itens if not it.get("evidencias")]
    if sem_evidencia:
        lista = "; ".join(sem_evidencia)
        raise ValueError(
            f"Os seguintes itens não têm evidência anexada: {lista}. "
            "Anexe a comprovação na aba Precificação antes de gerar este PDF."
        )

    data_emissao = datetime.now().strftime("%d/%m/%Y")
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    writer = PdfWriter()

    # 1) Páginas de memória de cálculo
    memory_bytes = _build_memory_pdf_bytes(itens, responsavel, data_emissao)
    for page in PdfReader(io.BytesIO(memory_bytes)).pages:
        writer.add_page(page)

    # 2) Páginas de evidência, item a item
    for it in itens:
        desc = it.get("descricao") or "Item"
        for evid in it.get("evidencias") or []:
            nome = evid.get("nome", "evidencia")
            tipo = evid.get("tipo")
            conteudo = evid.get("bytes")
            if not conteudo:
                continue
            try:
                if tipo == "imagem":
                    page_bytes = _build_image_evidence_page_bytes(desc, nome, conteudo)
                    pages_to_add = list(PdfReader(io.BytesIO(page_bytes)).pages)
                elif tipo == "pdf":
                    header_bytes = _build_pdf_evidence_header_bytes(desc, nome)
                    header_pages = list(PdfReader(io.BytesIO(header_bytes)).pages)
                    merged_pages = list(PdfReader(io.BytesIO(conteudo)).pages)
                    pages_to_add = header_pages + merged_pages
                else:
                    pages_to_add = []
                for page in pages_to_add:
                    writer.add_page(page)
            except Exception:
                # Um anexo corrompido não derruba o restante do documento.
                # Importante: nada parcial do anexo com falha é adicionado —
                # só a página de aviso, para não duplicar cabeçalho + erro.
                err_bytes = _build_pdf_evidence_header_bytes(
                    desc, f"{nome} (não foi possível processar este arquivo)"
                )
                for page in PdfReader(io.BytesIO(err_bytes)).pages:
                    writer.add_page(page)

    with open(output_path, "wb") as fh:
        writer.write(fh)

    return output_path
