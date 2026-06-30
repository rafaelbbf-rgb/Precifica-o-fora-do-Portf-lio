# Guia de Publicação — Calculadora de Precificação Office Total

Como colocar a ferramenta na web, **de graça** e com **acesso protegido por senha**,
usando o **Streamlit Community Cloud**. Não precisa usar nenhum comando — tudo pela
interface do navegador.

Tempo estimado: 15–20 minutos.

---

## Visão geral

1. Criar conta no GitHub e enviar o projeto (repositório **público** pode, sem risco).
2. Conectar o Streamlit Community Cloud ao GitHub e publicar o app.
3. Configurar **login** e **coeficiente** nos Secrets (ficam fora do código).
4. Compartilhar o link + login com o time.

> Segurança: senha, usuário e coeficiente NÃO ficam no código — são lidos dos
> Secrets do Streamlit. Por isso o repositório pode ser público: no máximo
> alguém vê a lógica genérica, nunca os dados sensíveis. O acesso ao app é
> sempre travado por login.

---

## Parte 1 — Enviar o projeto para o GitHub

1. Crie uma conta gratuita em **https://github.com** (se ainda não tiver).
2. Clique no **+** no canto superior direito → **New repository**.
3. Dê um nome (ex.: `precificacao-office-total`). Pode deixar **Public**
   (nada sensível fica no código) e clique em **Create repository**.
4. Na página do repositório, clique em **"uploading an existing file"**
   (ou **Add file → Upload files**).
5. **Arraste todos os arquivos e pastas do projeto** para a área de upload.
   - Inclua: `app.py`, `requirements.txt`, `README.md`, e as pastas `src/`,
     `assets/`, `.streamlit/`, `output/`, `tests/`.
   - **NÃO** envie a pasta `.venv/` (se existir) nem um eventual
     `.streamlit/secrets.toml` (os valores reais nunca vão para o GitHub).
   - O arquivo `.streamlit/secrets.toml.example` **pode** ser enviado (é só um modelo).
6. Clique em **Commit changes**.

> Dica: o arquivo `.gitignore` já vem configurado para ignorar `.venv`, cache e a
> senha. Se subir tudo de uma vez pela web, apenas evite manualmente a pasta `.venv`.

---

## Parte 2 — Publicar no Streamlit Community Cloud

1. Acesse **https://share.streamlit.io** (ou https://streamlit.io/cloud).
2. Clique em **Continue with GitHub** e autorize o acesso.
   - Para repositórios **privados**, o GitHub vai pedir uma permissão extra de
     leitura — é normal e necessário.
3. Clique em **Create app** → **Deploy a public app from GitHub** (serve para
   repositórios privados também).
4. Preencha:
   - **Repository:** `seu-usuario/precificacao-office-total`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Clique em **Deploy**. Em 2–5 minutos o app fica no ar com um endereço como
   `https://precificacao-office-total.streamlit.app`.

---

## Parte 3 — Configurar usuários e coeficiente (Secrets)

Como nada sensível fica no código, você define tudo em **Secrets**:

1. No painel do app (https://share.streamlit.io), abra o menu **⋮** do app →
   **Settings** → **Secrets**.
2. Cole e ajuste — pode adicionar **quantos usuários quiser**, um por linha:

   ```toml
   [credentials]
   rb = "uma-senha-forte"
   vendedor1 = "outra-senha"
   vendedor2 = "mais-uma-senha"

   default_coefficient_36m = 0.05
   ```

3. Clique em **Save**. O app reinicia e passa a aceitar o login de todos os
   usuários listados.

### Para adicionar um novo usuário depois

Volte em **Settings → Secrets**, acrescente uma linha dentro de
`[credentials]` (ex.: `vendedor3 = "senha-dele"`) e clique em **Save**. Não
precisa tocar no código — é só essa edição.

### Para remover o acesso de alguém

Apague a linha correspondente em **Secrets** e clique em **Save**. A pessoa
não conseguirá mais entrar.

> Enquanto nenhuma credencial for configurada, o app mostra um aviso de
> "configuração pendente" e não libera o acesso — ninguém entra sem login.
>
> Como **nada sensível fica no código**, o repositório pode ser **público** sem
> expor senha nem coeficiente. No máximo, alguém vê a lógica genérica do app.

Cada pessoa logada vê "Conectado como [usuário]" no topo do app, com um botão
**Sair** para encerrar a sessão.

---

## Parte 4 — Restringir ainda mais (opcional)

Se quiser limitar por e-mail (além da senha):

1. No painel do app → **Settings** → **Sharing**.
2. Defina o app como **privado** e adicione os **e-mails** das pessoas
   autorizadas. Só elas conseguirão abrir (precisam entrar com a conta).

A senha sozinha já costuma ser suficiente para uso comercial do dia a dia.

---

## Atualizar a ferramenta depois

Sempre que quiser mudar algo (coeficiente, textos, visual):

1. Edite o arquivo no GitHub (ou suba uma versão nova).
2. Faça **Commit**. O Streamlit detecta e **atualiza o app automaticamente**.

---

## Bom saber (plano gratuito)

- A ferramenta é leve e funciona com folga dentro do plano gratuito.
- Apps pouco usados podem "dormir"; ao abrir o link, levam alguns segundos para
  reativar. É normal.
- Você pode publicar mais de um app gratuito na mesma conta.

---

## Resolução de problemas

- **"Error installing requirements"**: confirme que o `requirements.txt` foi enviado
  na raiz do repositório.
- **App não acha o logo**: confirme que a pasta `assets/` (com `logo.png` e
  `logo_white.png`) foi enviada.
- **Pediu senha e não aceita**: verifique em Settings → Secrets se a linha
  `app_password = "..."` está exatamente nesse formato (com aspas).
- **App "dormindo"**: clique em reativar e aguarde alguns segundos.
