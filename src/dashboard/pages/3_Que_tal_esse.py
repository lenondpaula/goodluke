# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
from pathlib import Path
import sys

import streamlit as st

# Disponibiliza o módulo loja.py do app específico
BASE_DIR = Path(__file__).resolve().parents[3]
APP_DIR = BASE_DIR / "sistema-recomendacao" / "app"
sys.path.insert(0, str(APP_DIR))

from loja import render_app  # noqa: E402


st.set_page_config(
    page_title="Que tal esse? | Recomendador",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app()
