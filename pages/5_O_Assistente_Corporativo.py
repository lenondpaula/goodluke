"""
Página ponte para o Assistente Corporativo RAG
Integra o submódulo assistente-rag ao Hub de Criação
"""

from pathlib import Path
import sys

import streamlit as st

# Disponibiliza o módulo chatbot_rag.py do app específico
APP_DIR = Path(__file__).resolve().parents[1] / "assistente-rag" / "app"
sys.path.insert(0, str(APP_DIR))

from chatbot_rag import render_app  # noqa: E402


st.set_page_config(
    page_title="Assistente Corporativo | RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app()
