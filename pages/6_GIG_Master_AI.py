# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
App 6 — GIG-Master AI
Planejamento Inteligente de Turnês Musicais
Combina análise preditiva + IA generativa para otimização de shows
"""

import sys
from pathlib import Path

import streamlit as st

# Configuração de paths para importar o submódulo
BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "projeto-gig-master" / "app"
SRC_DIR = BASE_DIR / "projeto-gig-master" / "src"

# Adicionar diretórios ao path
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(SRC_DIR))

from gig_dashboard import render_app  # noqa: E402

# Executar o dashboard
render_app()
