"""
auth.py
-------
Tela de login (usuário + senha). Versão segura para repositório PÚBLICO:
as credenciais NÃO ficam no código — são lidas apenas de:

  - st.secrets["app_username"] / st.secrets["app_password"]  (Streamlit Cloud), ou
  - variáveis de ambiente APP_USERNAME / APP_PASSWORD (uso local).

Se nada estiver configurado, o app fica bloqueado com instruções (não há senha
padrão exposta no código).
"""

import os

from .ui_components import render_header, render_note


def _credentials():
    import streamlit as st

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
    return user, pwd


def require_login() -> bool:
    """Retorna True se autenticado; senão desenha o login e retorna False."""
    import streamlit as st

    exp_user, exp_pwd = _credentials()

    st.markdown("<div style='max-width:440px;margin:8vh auto 0'>", unsafe_allow_html=True)

    if not exp_user or not exp_pwd:
        render_header("Configuração pendente", "Calculadora de Precificação · Office Total")
        render_note(
            "As credenciais ainda não foram configuradas. Defina <b>app_username</b> e "
            "<b>app_password</b> em <b>Settings → Secrets</b> no Streamlit (ou nas variáveis "
            "de ambiente APP_USERNAME / APP_PASSWORD).", "warn",
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
        if usuario.strip() == exp_user and senha == exp_pwd:
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    st.caption("Ferramenta de uso interno do Grupo Office Total.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False
