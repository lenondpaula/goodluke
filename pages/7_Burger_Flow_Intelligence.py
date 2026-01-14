"""
App 7 — Burger-Flow Intelligence
Dashboard de gestão inteligente para hamburguerias
Combina Análise Preditiva + Engenharia de Menu (BCG)
"""

import sys
from pathlib import Path

import streamlit as st

# Configuração de paths para importar o submódulo
BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "projeto-burger-flow" / "app"
SRC_DIR = BASE_DIR / "projeto-burger-flow" / "src"

# Adicionar diretórios ao path
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(SRC_DIR))

from burger_dashboard import render_app  # noqa: E402

# Executar o dashboard
render_app()
