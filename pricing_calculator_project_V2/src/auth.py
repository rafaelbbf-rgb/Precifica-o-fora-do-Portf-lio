"""
auth.py
-------
Tela de senha simples para proteger o app quando publicado na web.

A senha NÃO fica no código. Ela é lida de:
  1. st.secrets["app_password"]  (configurada no Streamlit Community Cloud), ou
  2. variável de ambiente APP_PASSWORD.

Se nenhuma senha estiver configurada (ex.: rodando localmente), o app libera
o acesso direto — assim o uso local continua sem fricção.
"""

import os

from .ui_components import render_header


def _expected_password():
    import streamlit as st

    try:
        if "app_password" in st.secrets:
            valor = st.secrets["app_password"]
            if valor:
                return str(valor)
    except Exception:
        pass
    return os.environ.get("APP_PASSWORD")


def require_login() -> bool:
    """
    Retorna True se o acesso está liberado. Caso contrário, desenha a tela de
    login e retorna False (o app deve então chamar st.stop()).
    """
    import streamlit as st

    expected = _expected_password()
    if not expected:
        return True  # nenhuma senha definida -> uso local liberado
    if st.session_state.get("auth_ok"):
        return True

    st.markdown("<div style='max-width:440px;margin:8vh auto 0'>", unsafe_allow_html=True)
    render_header("Acesso restrito", "Calculadora de Precificação · Office Total")
    st.write("")
    senha = st.text_input("Senha de acesso", type="password", key="login_pwd")
    if st.button("Entrar"):
        if senha == expected:
            st.session_state["auth_ok"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.caption("Ferramenta de uso interno do Grupo Office Total.")
    st.markdown("</div>", unsafe_allow_html=True)
    return False
