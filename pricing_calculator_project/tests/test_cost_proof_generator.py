"""
Testes do gerador de PDF de Comprovação de Custo (cost_proof_generator).

Cobre: validações (itens vazios, evidência ausente), geração combinando
memória de cálculo + evidência em imagem + evidência em PDF mesclado, e
tratamento de anexos corrompidos sem derrubar o restante do documento.

Observação: a fixture de imagem usa Pillow, já instalado como dependência
transitiva do ReportLab — não é necessário adicioná-lo ao requirements.txt.
Os testes usam um coeficiente genérico (5%), no mesmo padrão dos demais
arquivos de teste do projeto.
"""

import io
import os
import sys

import pytest
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdfcanvas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cost_proof_generator import generate_cost_proof_report
from src.price_calculator import calculate_prices_from_cost

COEF = 0.05  # coeficiente genérico para os testes


# --------------------------------------------------------------------------- #
# Fixtures auxiliares (imagem e PDF sintéticos, sem depender de arquivos)     #
# --------------------------------------------------------------------------- #
def _fake_jpeg_bytes() -> bytes:
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (400, 300), color=(210, 220, 235)).save(buf, format="JPEG")
    return buf.getvalue()


def _fake_pdf_bytes(n_pages: int = 2) -> bytes:
    buf = io.BytesIO()
    c = pdfcanvas.Canvas(buf, pagesize=A4)
    for i in range(n_pages):
        c.drawString(50, 800, f"Cotação Fornecedor - Página {i + 1}")
        c.showPage()
    c.save()
    return buf.getvalue()


def _item_por_custo(descricao="Servidor fora de portfólio", quantidade=1,
                     custo=10000.0, coef=COEF, evidencias=None):
    return {
        "descricao": descricao, "quantidade": quantidade, "fixo": False,
        "custo": custo, "coef": coef,
        "valores": calculate_prices_from_cost(custo, coef),
        "evidencias": evidencias if evidencias is not None else [],
    }


def _item_taxa_fixa(descricao="Licença especial", quantidade=10, valor=55.0,
                     evidencias=None):
    return {
        "descricao": descricao, "quantidade": quantidade, "fixo": True,
        "valores": {k: valor for k in
                    ("preco_12m", "preco_24m", "preco_36m", "preco_48m", "preco_60m")},
        "evidencias": evidencias if evidencias is not None else [],
    }


def _evid_imagem(nome="foto.jpg"):
    return {"nome": nome, "tipo": "imagem", "bytes": _fake_jpeg_bytes()}


def _evid_pdf(nome="cotacao.pdf", n_pages=2):
    return {"nome": nome, "tipo": "pdf", "bytes": _fake_pdf_bytes(n_pages)}


# --------------------------------------------------------------------------- #
# Validações                                                                  #
# --------------------------------------------------------------------------- #
def test_lista_vazia_levanta_erro(tmp_path):
    with pytest.raises(ValueError):
        generate_cost_proof_report([], "Rafael Borja", str(tmp_path / "out.pdf"))


def test_item_sem_evidencia_levanta_erro(tmp_path):
    item = _item_por_custo(evidencias=[])
    with pytest.raises(ValueError, match="evidência"):
        generate_cost_proof_report([item], "Rafael Borja", str(tmp_path / "out.pdf"))


def test_item_com_evidencias_none_levanta_erro(tmp_path):
    item = _item_por_custo()
    item["evidencias"] = None
    with pytest.raises(ValueError):
        generate_cost_proof_report([item], "Rafael Borja", str(tmp_path / "out.pdf"))


def test_mensagem_de_erro_identifica_o_item_pendente(tmp_path):
    com_evidencia = _item_por_custo(descricao="Item OK", evidencias=[_evid_imagem()])
    sem_evidencia = _item_taxa_fixa(descricao="Item Pendente", evidencias=[])
    with pytest.raises(ValueError) as exc:
        generate_cost_proof_report([com_evidencia, sem_evidencia], "Rafael", str(tmp_path / "out.pdf"))
    assert "Item Pendente" in str(exc.value)
    assert "Item OK" not in str(exc.value)


def test_bloqueia_se_item_taxa_fixa_estiver_sem_evidencia(tmp_path):
    """A validação cobre TODOS os itens, inclusive os de taxa fixa."""
    item_fixo_sem_evidencia = _item_taxa_fixa(evidencias=[])
    with pytest.raises(ValueError):
        generate_cost_proof_report([item_fixo_sem_evidencia], "Rafael", str(tmp_path / "out.pdf"))


# --------------------------------------------------------------------------- #
# Geração — caminho feliz                                                     #
# --------------------------------------------------------------------------- #
def test_gera_pdf_com_item_por_custo_e_evidencia_imagem(tmp_path):
    item = _item_por_custo(evidencias=[_evid_imagem()])
    out = str(tmp_path / "comprovacao.pdf")
    resultado = generate_cost_proof_report([item], "Rafael Borja", out)
    assert resultado == out
    assert os.path.exists(out)
    assert os.path.getsize(out) > 1000

    reader = PdfReader(out)
    # 1 página de memória + 1 página de evidência (imagem) = 2
    assert len(reader.pages) == 2


def test_gera_pdf_com_item_taxa_fixa_e_evidencia_pdf_mesclada(tmp_path):
    item = _item_taxa_fixa(evidencias=[_evid_pdf(n_pages=3)])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)

    reader = PdfReader(out)
    # 1 página de memória + 1 cabeçalho + 3 páginas mescladas do PDF = 5
    assert len(reader.pages) == 5


def test_gera_pdf_multi_item_com_evidencias_mistas(tmp_path):
    item1 = _item_por_custo(descricao="Servidor", evidencias=[_evid_imagem()])
    item2 = _item_taxa_fixa(descricao="Licença", evidencias=[_evid_pdf(n_pages=2)])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item1, item2], "Rafael Borja", out)

    reader = PdfReader(out)
    # 1 memória + 1 imagem + (1 cabeçalho + 2 páginas mescladas) = 5
    assert len(reader.pages) == 5


def test_item_com_multiplas_evidencias(tmp_path):
    item = _item_por_custo(evidencias=[_evid_imagem("foto1.jpg"), _evid_imagem("foto2.jpg")])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)

    reader = PdfReader(out)
    # 1 memória + 2 páginas de imagem = 3
    assert len(reader.pages) == 3


def test_tamanhos_de_pagina_mistos_paisagem_e_retrato(tmp_path):
    """Página de memória fica em paisagem; páginas de evidência ficam em retrato."""
    item = _item_por_custo(evidencias=[_evid_imagem()])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)

    reader = PdfReader(out)
    pag_memoria = reader.pages[0]
    pag_evidencia = reader.pages[1]
    assert float(pag_memoria.mediabox.width) > float(pag_memoria.mediabox.height)
    assert float(pag_evidencia.mediabox.width) < float(pag_evidencia.mediabox.height)


def test_cria_diretorio_de_saida_se_nao_existir(tmp_path):
    item = _item_por_custo(evidencias=[_evid_imagem()])
    out = str(tmp_path / "subpasta" / "nova" / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)
    assert os.path.exists(out)


def test_responsavel_vazio_usa_padrao_sem_erro(tmp_path):
    item = _item_por_custo(evidencias=[_evid_imagem()])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "", out)
    assert os.path.exists(out)


# --------------------------------------------------------------------------- #
# Robustez — anexos corrompidos não derrubam o documento                      #
# --------------------------------------------------------------------------- #
def test_pdf_de_evidencia_corrompido_nao_quebra_geracao(tmp_path):
    item = _item_por_custo(evidencias=[
        {"nome": "corrompido.pdf", "tipo": "pdf", "bytes": b"isto nao e um pdf valido"}
    ])
    out = str(tmp_path / "comprovacao.pdf")
    # Não deve levantar exceção — o anexo corrompido vira uma única página de aviso
    # (sem duplicar um cabeçalho de sucesso antes do erro).
    generate_cost_proof_report([item], "Rafael Borja", out)
    reader = PdfReader(out)
    assert len(reader.pages) == 2  # memória + página de aviso


def test_imagem_de_evidencia_corrompida_nao_quebra_geracao(tmp_path):
    item = _item_por_custo(evidencias=[
        {"nome": "imagem_ruim.jpg", "tipo": "imagem", "bytes": b"nao e uma imagem valida"}
    ])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)
    reader = PdfReader(out)
    assert len(reader.pages) == 2  # memória + página com aviso de imagem ilegível


def test_evidencia_com_bytes_vazios_e_ignorada_sem_quebrar(tmp_path):
    item = _item_por_custo(evidencias=[{"nome": "vazio.jpg", "tipo": "imagem", "bytes": b""}])
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item], "Rafael Borja", out)
    reader = PdfReader(out)
    assert len(reader.pages) == 1  # só a página de memória; anexo vazio é ignorado


def test_um_anexo_corrompido_nao_afeta_os_demais_itens(tmp_path):
    """Um anexo ruim em um item não deve impedir a evidência válida de outro item."""
    item_ok = _item_por_custo(descricao="Item OK", evidencias=[_evid_imagem()])
    item_corrompido = _item_taxa_fixa(
        descricao="Item com anexo ruim",
        evidencias=[{"nome": "ruim.pdf", "tipo": "pdf", "bytes": b"lixo"}],
    )
    out = str(tmp_path / "comprovacao.pdf")
    generate_cost_proof_report([item_ok, item_corrompido], "Rafael Borja", out)
    reader = PdfReader(out)
    # 1 memória + 1 (imagem válida do item OK) + 1 (aviso do item corrompido) = 3
    assert len(reader.pages) == 3
