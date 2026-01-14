# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
App 8 — PoA-Insight Explorer
Turismo inteligente em Porto Alegre com recomendações contextuais
Mapa interativo + Filtros por clima, horário e perfil
"""

import sys
from pathlib import Path

import streamlit as st

# Configuração de paths para importar o submódulo
BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "projeto-poa-explorer" / "app"
SRC_DIR = BASE_DIR / "projeto-poa-explorer" / "src"

# Adicionar diretórios ao path
sys.path.insert(0, str(APP_DIR))
sys.path.insert(0, str(SRC_DIR))

from poa_dashboard import render_app  # noqa: E402

# Executar o dashboard
render_app()
