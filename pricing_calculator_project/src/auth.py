"""
auth.py
-------
Tela de login (usuário + senha), com suporte a MÚLTIPLOS usuários.

As credenciais NÃO ficam no código — são lidas apenas de:

  - st.secrets["credentials"]  → tabela com vários pares usuário = "senha"
    (formato recomendado, suporta quantos usuários você quiser), ou
  - st.secrets["app_username"] / st.secrets["app_password"]  → um único
    usuário (formato antigo, mantido por compatibilidade), ou
  - variáveis de ambiente APP_USERNAME / APP_PASSWORD (uso local).

Se nada estiver configurado, o app fica bloqueado com instruções.
"""

import os

from .ui_components import render_header, render_note

# Chaves que podem acabar aninhadas dentro de [credentials] por engano (por
# causa de como o TOML funciona) e que NUNCA devem ser tratadas como um par
# usuário/senha de login válido.
_RESERVED_KEYS = {"admin_users", "default_coefficient_36m"}


def _credentials_map():
    """Retorna um dict {usuario: senha} com todas as credenciais válidas."""
    import streamlit as st

    creds = {}
    try:
        if "credentials" in st.secrets:
            creds = {
                str(k): str(v) for k, v in dict(st.secrets["credentials"]).items()
                if str(k) not in _RESERVED_KEYS
            }
    except Exception:
        creds = {}

    if not creds:
        user = None
        pwd = None
        try:
            if "app_username" in st.secrets:
                user = str(st.secrets["app_username"])
            if "app_password" in st.secrets:
                pwd = str(st.secrets["app_password"])
        except Exception:
            pass
        user = user or os.environ.get("APP_USERNAME")
        pwd = pwd or os.environ.get("APP_PASSWORD")
        if user and pwd:
            creds = {user: pwd}

    return creds


def require_login() -> bool:
    """Retorna True se autenticado; senão desenha o login e retorna False."""
    import streamlit as st

    creds = _credentials_map()

    st.markdown("<div style='max-width:440px;margin:8vh auto 0'>", unsafe_allow_html=True)

    if not creds:
        render_header("Configuração pendente", "Calculadora de Precificação · Office Total")
        render_note(
            "Nenhuma credencial configurada. Defina <b>[credentials]</b> (ou "
            "<b>app_username</b>/<b>app_password</b>) em <b>Settings → Secrets</b> no Streamlit.",
            "warn",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return False

    if st.session_state.get("auth_ok"):
        return True

    render_header("Acesso restrito", "Calculadora de Precificação · Office Total")
    st.write("")
    usuario = st.text_input("Usuário", key="login_user")
    senha = st.text_input("Senha", type="password", key="login_pwd")
    if st.button("Entrar"):
        if usuario.strip() in creds and creds[usuario.strip()] == senha:
            st.session_state["auth_ok"] = True
            st.session_state["auth_user"] = usuario.strip()
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.caption("Ferramenta de uso interno do Grupo Office Total.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False


def render_logout() -> None:
    """Mostra quem está logado e um botão para sair (opcional, no topo do app)."""
    import streamlit as st

    user = st.session_state.get("auth_user")
    if not user:
        return
    c1, c2 = st.columns([6, 1])
    with c1:
        st.caption(f"Conectado como **{user}**")
    with c2:
        if st.button("Sair", key="logout_btn"):
            st.session_state.pop("auth_ok", None)
            st.session_state.pop("auth_user", None)
            st.rerun()


def is_admin_user(username: str) -> bool:
    """
    Retorna True se o usuário tem acesso total: coeficiente visível/editável,
    aba Cálculo Reverso e aba Comprovação de Custo (memória de cálculo).

    Lido de st.secrets["admin_users"] (lista de usuários) ou da variável de
    ambiente ADMIN_USERS (separada por vírgula).

    Se esta lista NÃO estiver configurada em nenhum lugar, TODOS os usuários
    são tratados como admin (preserva o comportamento atual) — a restrição
    só passa a valer quando admin_users é definida explicitamente.
    """
    import streamlit as st

    admins = None
    try:
        if "admin_users" in st.secrets:
            admins = [str(a) for a in list(st.secrets["admin_users"])]
        elif "credentials" in st.secrets and "admin_users" in st.secrets["credentials"]:
            # Compatibilidade: formatos antigos do guia podiam aninhar esta
            # chave dentro de [credentials] por engano (comportamento do TOML).
            admins = [str(a) for a in list(st.secrets["credentials"]["admin_users"])]
    except Exception:
        admins = None
    if admins is None:
        env = os.environ.get("ADMIN_USERS")
        if env:
            admins = [a.strip() for a in env.split(",") if a.strip()]
    if admins is None:
        return True  # ninguém configurado -> sem restrição (compatibilidade)
    return (username or "") in admins
