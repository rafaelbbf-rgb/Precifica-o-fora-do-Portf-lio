# Calculadora Executiva de Precificação — Office Total

Ferramenta interna, leve e premium para precificar a **locação de equipamentos**
(modelo *Tecnologia por Assinatura* / HaaS) da Office Total. Calcula o valor mensal
de locação a partir do custo, gera uma **proposta executiva em PDF** com a
identidade visual da marca e ainda faz **cálculo reverso** (descobrir a base de
custo a partir do preço de 36 meses).

Construída em **Streamlit** com CSS customizado para parecer um produto interno
institucional — não a interface padrão do Streamlit.

---

## Índice
1. [Objetivo](#objetivo)
2. [Instalação](#instalação)
3. [Como rodar](#como-rodar)
4. [Como funciona a precificação](#como-funciona-a-precificação)
5. [Como funciona o cálculo reverso](#como-funciona-o-cálculo-reverso)
6. [Relatório executivo](#relatório-executivo)
7. [Regras de cálculo](#regras-de-cálculo)
8. [Como trocar o logo](#como-trocar-o-logo)
9. [Como alterar a paleta de cores](#como-alterar-a-paleta-de-cores)
10. [Documentos de identidade visual](#documentos-de-identidade-visual)
11. [Limitações](#limitações)
12. [Instruções para Windows](#instruções-para-windows)

---

## Objetivo

Dar ao time comercial uma **calculadora rápida de um equipamento por vez**, com:

- cálculo do preço mensal de locação para **12, 24, 36, 48 e 60 meses**;
- coeficiente de 36 meses ajustável na própria tela;
- resultado em **cards executivos**;
- **proposta em PDF** pronta para envio, sem expor nenhuma informação interna
  (custo, coeficiente ou fórmula);
- **cálculo reverso** para simulação interna.

Não é um sistema de tabela de preços, importação em massa ou dashboard. É uma
calculadora enxuta para o dia a dia.

---

## Instalação

Pré-requisito: **Python 3.10+**.

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

# 2. Instale as dependências
pip install -r requirements.txt
```

---

## Como rodar

### Opção 1 — Um clique (recomendado)

Dê **duplo clique** no arquivo:

- **Windows:** `Abrir Calculadora.bat`
- **macOS:** `Abrir Calculadora.command`
- **Linux:** `abrir_calculadora.sh`

Na primeira vez ele prepara o ambiente automaticamente (1–2 min) e abre o app no
navegador. Nas próximas vezes abre na hora. Para fechar, feche a janela preta.

> Pré-requisito único: ter o **Python 3.10+** instalado. No Windows, marque
> "Add Python to PATH" durante a instalação do Python.

### Opção 2 — Linha de comando

```bash
streamlit run app.py
```

O navegador abre direto na página **Precificação** (`http://localhost:8501`).

---

## Como funciona a precificação

Quem usa: o **gerente**, para precificar itens **fora de portfólio** e montar uma
proposta com **um ou mais itens**.

Para cada item, na aba **Precificação**:

1. Informe a **descrição** (linha única) e a **quantidade**.
2. Escolha o tipo:
   - **Por custo** — informe o custo unitário (privado) e o coeficiente; o sistema
     calcula os cinco prazos.
   - **Taxa fixa** — informe um valor mensal fixo por unidade (igual em todos os
     prazos), útil para licenças (ex.: Windows Server, Microsoft 365).
3. Clique em **Adicionar item**. Repita para quantos itens quiser.

A proposta aparece numa **tabela horizontal** (prazos nas colunas) com uma linha de
**Total mensal**. Os valores exibidos já consideram a quantidade. Você pode remover
itens ou limpar tudo. O **custo** aparece só na tela do gerente — **nunca** no PDF.

---

## Como funciona o cálculo reverso

Página de **simulação interna**. Você informa o **preço mensal de 36 meses** e o
coeficiente, e o sistema calcula a **base/custo estimado** do equipamento, além de
recalcular os demais prazos.

> Esta página **não gera PDF** — é apenas para uso interno.

---

## Relatório do vendedor (PDF)

Gera um documento **interno de consulta** em **PDF horizontal (paisagem)**, para o
vendedor usar em itens fora de portfólio, com a identidade Office Total:

- faixa marinho com logo branco e selo **"Uso interno · Consulta do vendedor"**;
- título **"Referência de Precificação de Locação"** e **data automática**;
- **tabela horizontal** com todos os itens, prazos nas colunas (12/24/36/48/60),
  coluna de **36 meses destacada**, itens de **taxa fixa** em destaque e linha de
  **Total mensal**;
- assinatura do responsável;
- rodapé de uso interno.

O PDF **não exibe**: custo, coeficiente, margem ou fórmula — apenas os **preços**
que o vendedor pode usar com o cliente.

Os PDFs são salvos em `output/relatorios/`.

---

## Regras de cálculo

**A partir do custo:**

```
preco_36m = custo × coeficiente_36m   (coeficiente padrão = 0.065)
preco_24m = preco_36m × 1.10
preco_12m = preco_24m × 1.10
preco_48m = preco_36m × 0.90
preco_60m = preco_48m × 0.90
```

**Cálculo reverso (a partir do preço de 36 meses):**

```
custo_estimado = preco_36m / coeficiente_36m
preco_24m = preco_36m × 1.10
preco_12m = preco_24m × 1.10
preco_48m = preco_36m × 0.90
preco_60m = preco_48m × 0.90
```

**Exemplo** — custo R$ 3.000,00 (coeficiente 6,5%):

| Prazo | Valor mensal |
|------:|-------------:|
| 12 meses | R$ 235,95 |
| 24 meses | R$ 214,50 |
| 36 meses | R$ 195,00 |
| 48 meses | R$ 175,50 |
| 60 meses | R$ 157,95 |

---

## Como trocar o logo

Substitua os arquivos na pasta `assets/`:

- `assets/logo.png` — logo colorido, usado no **cabeçalho do app**.
- `assets/logo_white.png` — logo branco, usado na **faixa marinho do PDF**.

Use PNG com fundo transparente. Não é preciso mexer no código.

---

## Como alterar a paleta de cores

Todas as cores ficam centralizadas em **`src/theme.py`**, em constantes:

```python
PRIMARY_COLOR    = "#19396A"
PRIMARY_DARK     = "#002060"
SECONDARY_COLOR  = "#007DAA"
ACCENT_COLOR     = "#12ABC2"
ACCENT_BRIGHT    = "#00B4C3"
BACKGROUND_COLOR = "#F5F7FA"
CARD_BACKGROUND  = "#FFFFFF"
BORDER_COLOR     = "#E2E8F0"
TEXT_COLOR       = "#1A2333"
MUTED_TEXT_COLOR = "#6B7280"
SUCCESS_COLOR    = "#2BA872"
WARNING_COLOR    = "#E8A33D"
```

Alterar uma constante repercute automaticamente na interface **e** no relatório.

---

## Documentos de identidade visual

A paleta deste projeto foi **extraída diretamente** dos arquivos oficiais da
Office Total (papel timbrado `.docx` e template `.pptx`):

- marinho institucional `#19396A` e marinho profundo `#002060` (logo / master do PPT);
- ciano/turquesa `#12ABC2` e `#00B4C3` (símbolo e palavra "GRUPO");
- azuis de apoio `#007DAA` / `#1281A6` (degradê do símbolo).

Para atualizar a identidade no futuro: extraia as novas cores do material oficial
e ajuste `src/theme.py`; troque os logos em `assets/`.

---

## Limitações

- Calcula **um equipamento por vez** (por design — é uma calculadora, não uma base).
- Sem importação de Excel/PDF, sem histórico, sem dashboard.
- O coeficiente e as regras de ajuste por prazo são parâmetros comerciais —
  revise antes de usar em proposta oficial.
- O PDF é otimizado para A4/impressão.

---

## Instruções para Windows

```powershell
# Criar ambiente virtual
python -m venv .venv

# Ativar
.venv\Scripts\activate

# Se o PowerShell bloquear a ativação, rode uma vez (como usuário):
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# Instalar dependências
pip install -r requirements.txt

# Rodar
streamlit run app.py
```

Os PDFs gerados ficam em `output\relatorios\`.
