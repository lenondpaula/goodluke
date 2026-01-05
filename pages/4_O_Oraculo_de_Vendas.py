"""
Página ponte para o Oráculo de Vendas
Integra o submódulo oraculo-vendas ao Hub de Criação
"""

from pathlib import Path
import sys

import streamlit as st

# Disponibiliza o módulo dashboard_vendas.py do app específico
APP_DIR = Path(__file__).resolve().parents[1] / "oraculo-vendas" / "app"
sys.path.insert(0, str(APP_DIR))

from dashboard_vendas import render_app  # noqa: E402


st.set_page_config(
    page_title="Oráculo de Vendas | BI Preditivo",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app()
