# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
PoA-Insight Explorer - Dashboard de Turismo Inteligente
Interface Streamlit com mapa interativo Folium
"""

from pathlib import Path
import sys

import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
import streamlit as st
from streamlit_folium import st_folium

# Adiciona src ao path para imports
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from motor_turismo import (  # type: ignore  # noqa: E402
    recomendar_roteiro,
    gerar_zonas_calor,
    carregar_locais,
    PERFIL_CATEGORIAS,
)
from shared.components import (  # noqa: E402
    SHARED_SIDEBAR_CSS,
    render_sidebar_navegacao,
    render_rodape,
    render_instrucoes_uso,
)

# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista (padrão do Hub)
# ────────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
:root {
    --primary: #0f172a;
    --secondary: #334155;
    --accent: #1d4ed8;
    --success: #16a34a;
    --danger: #dc2626;
    --warning: #d97706;
    --bg: #f8fafc;
}
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.block-container {
    padding-top: 2rem;
    max-width: 1400px;
}
h1 {
    color: var(--primary);
    font-weight: 700;
    letter-spacing: -0.5px;
}
section[data-testid="stSidebar"] {
    background: var(--primary);
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}
section[data-testid="stSidebar"] label {
    font-weight: 500;
}
.info-box {
    background: #f1f5f9;
    border-left: 4px solid #1d4ed8;
    padding: 1rem 1.25rem;
    border-radius: 6px;
    margin-bottom: 1.5rem;
}
.local-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}
.local-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.categoria-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 0.5rem;
}
.cat-parque { background: #dcfce7; color: #166534; }
.cat-museu { background: #dbeafe; color: #1e40af; }
.cat-gastronomia { background: #fef3c7; color: #92400e; }
.cat-vida-noturna { background: #fce7f3; color: #9d174d; }
.cat-cultura { background: #f3e8ff; color: #6b21a8; }
.weather-icon { font-size: 2rem; margin-bottom: 0.5rem; }
</style>
"""

# Cores para marcadores no mapa por categoria
CORES_CATEGORIA = {
    "Parque": "green",
    "Museu": "blue",
    "Gastronomia": "orange",
    "Vida Noturna": "pink",
    "Cultura": "purple",
}

# Ícones FontAwesome para cada categoria
ICONES_CATEGORIA = {
    "Parque": "tree",
    "Museu": "university",
    "Gastronomia": "utensils",
    "Vida Noturna": "glass-cheers",
    "Cultura": "theater-masks",
}

# Centro de Porto Alegre
POA_CENTER = [-30.0346, -51.2177]
POA_ZOOM = 13


@st.cache_data(show_spinner=False)
def carregar_dados_locais():
    """Carrega base de locais com cache."""
    return carregar_locais()


def criar_mapa_base() -> folium.Map:
    """Cria mapa base centralizado em Porto Alegre."""
    m = folium.Map(
        location=POA_CENTER,
        zoom_start=POA_ZOOM,
        tiles="CartoDB positron",  # Estilo limpo para visualização
    )
    return m


def adicionar_marcadores(mapa: folium.Map, df_locais: pd.DataFrame) -> folium.Map:
    """Adiciona marcadores coloridos por categoria."""
    for _, local in df_locais.iterrows():
        categoria = local["Categoria"]
        cor = CORES_CATEGORIA.get(categoria, "gray")
        icone = ICONES_CATEGORIA.get(categoria, "info")
        
        # Popup com informações
        popup_html = f"""
        <div style="width: 200px; font-family: 'Segoe UI', sans-serif;">
            <h4 style="margin: 0 0 8px 0; color: #0f172a;">{local['Nome']}</h4>
            <p style="margin: 0 0 4px 0; font-size: 12px; color: #64748b;">
                <strong>Categoria:</strong> {categoria}
            </p>
            <p style="margin: 0 0 4px 0; font-size: 12px; color: #64748b;">
                <strong>Tipo:</strong> {local['Tipo']}
            </p>
            <p style="margin: 0 0 4px 0; font-size: 12px; color: #64748b;">
                <strong>Preço:</strong> {'$' * int(local['Preco_Medio'])}
            </p>
            <p style="margin: 0 0 4px 0; font-size: 12px; color: #64748b;">
                <strong>Melhor horário:</strong> {local['Horario_Pico']}
            </p>
            <p style="margin: 8px 0 0 0; font-size: 11px; color: #475569;">
                {local.get('Descricao', '')}
            </p>
        </div>
        """
        
        folium.Marker(
            location=[local["Lat"], local["Lon"]],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(color=cor, icon=icone, prefix="fa"),
            tooltip=local["Nome"],
        ).add_to(mapa)
    
    return mapa


def adicionar_heatmap(mapa: folium.Map, horario: str) -> folium.Map:
    """Adiciona mapa de calor baseado no horário."""
    pontos_calor = gerar_zonas_calor(horario)
    
    if pontos_calor:
        heat_data = [[p["lat"], p["lon"], p["intensidade"]] for p in pontos_calor]
        
        HeatMap(
            heat_data,
            min_opacity=0.3,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={0.4: "blue", 0.65: "lime", 0.8: "yellow", 1: "red"},
        ).add_to(mapa)
    
    return mapa


def render_app():
    """Renderiza o dashboard principal."""
    st.set_page_config(
        page_title="PoA-Insight Explorer",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    st.title("🗺️ PoA-Insight Explorer")
    st.markdown("Turismo inteligente em Porto Alegre com recomendações contextuais")
    
    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Selecione seu perfil na sidebar",
            "Configure clima e horário atuais",
            "Explore o mapa interativo",
        ],
        ferramentas_sidebar=[
            "**Perfil**: Explorador, Natureza, Cultura, Gastronomia ou Festa",
            "**Clima**: Sol ou Chuva (filtra locais cobertos)",
            "**Horário**: Manhã, Tarde ou Noite",
            "**Heatmap**: Visualize concentração de pessoas",
        ]
    )
    
    # Descrição do sistema
    st.markdown(
        """
        <div class="info-box">
            <strong>O que é?</strong><br>
            Sistema de turismo inteligente que recomenda pontos de interesse em Porto Alegre
            baseado no seu perfil, condição climática e horário do dia.<br><br>
            <strong>Funcionalidades</strong><br>
            • <b>Filtro Contextual:</b> Recomendações adaptadas a chuva/sol e hora do dia<br>
            • <b>Mapa Interativo:</b> Visualização com marcadores coloridos por categoria<br>
            • <b>Mapa de Calor:</b> Mostra onde está o "buzz" em cada horário
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # ─────────────────────────────────────────────────────────────────────────
    # SIDEBAR - Controles
    # ─────────────────────────────────────────────────────────────────────────
    with st.sidebar:
        st.header("🎯 Seu Perfil")
        
        perfil = st.selectbox(
            "O que você curte?",
            options=["Explorador", "Natureza", "Cultura", "Gastronomia", "Festa"],
            index=0,
            help="Selecione seu perfil para recomendações personalizadas"
        )
        
        st.divider()
        
        st.header("🌤️ Condições Atuais")
        
        clima = st.radio(
            "Condição do Tempo",
            options=["☀️ Sol", "🌧️ Chuva"],
            index=0,
            help="Com chuva, apenas locais cobertos são recomendados"
        )
        clima_limpo = "Sol" if "Sol" in clima else "Chuva"
        
        horario = st.radio(
            "Hora do Dia",
            options=["🌅 Manhã", "☀️ Tarde", "🌙 Noite"],
            index=1,
            help="O horário afeta quais locais estão no pico de atividade"
        )
        horario_limpo = horario.split()[-1]  # "🌅 Manhã" -> "Manhã"
        
        st.divider()
        
        st.header("🗺️ Opções do Mapa")
        mostrar_heatmap = st.checkbox("Mostrar Mapa de Calor", value=True)
        mostrar_todos = st.checkbox("Mostrar Todos os Locais", value=False)
        
        st.divider()
        
        st.markdown("### 🏷️ Legenda")
        st.markdown("🟢 **Parque** — Áreas verdes")
        st.markdown("🔵 **Museu** — Arte e história")
        st.markdown("🟠 **Gastronomia** — Comida e bebida")
        st.markdown("🩷 **Vida Noturna** — Bares e festas")
        st.markdown("🟣 **Cultura** — Teatros e patrimônio")
    
    # ─────────────────────────────────────────────────────────────────────────
    # CONTEÚDO PRINCIPAL
    # ─────────────────────────────────────────────────────────────────────────
    
    # Carregar dados
    try:
        df_todos = carregar_dados_locais()
    except FileNotFoundError:
        st.error("⚠️ Base de locais não encontrada. Execute: `python src/gerar_locais_poa.py`")
        return
    
    # Obter recomendações
    df_recomendados = recomendar_roteiro(
        perfil_usuario=perfil,
        clima_atual=clima_limpo,
        hora_atual=horario_limpo,
        top_n=5,
        df_locais=df_todos
    )
    
    # Layout em duas colunas
    col_mapa, col_lista = st.columns([2, 1])
    
    with col_mapa:
        st.subheader("📍 Mapa de Porto Alegre")
        
        # Criar mapa
        mapa = criar_mapa_base()
        
        # Decidir quais locais mostrar
        if mostrar_todos:
            df_para_mapa = df_todos
            st.caption(f"Mostrando todos os {len(df_todos)} locais cadastrados")
        else:
            df_para_mapa = df_recomendados
            st.caption(f"Mostrando {len(df_recomendados)} locais recomendados para você")
        
        # Adicionar marcadores
        if not df_para_mapa.empty:
            mapa = adicionar_marcadores(mapa, df_para_mapa)
        
        # Adicionar heatmap
        if mostrar_heatmap:
            mapa = adicionar_heatmap(mapa, horario_limpo)
        
        # Renderizar mapa
        st_folium(mapa, width=None, height=500, returned_objects=[])
        
        # Contexto do mapa de calor
        if mostrar_heatmap:
            zonas_texto = {
                "Manhã": "Centro Histórico e Mercado Público (movimento comercial)",
                "Tarde": "Orla do Guaíba e Redenção (lazer e pôr do sol)",
                "Noite": "Cidade Baixa e Padre Chagas (vida noturna)",
            }
            st.info(f"🔥 **Concentração de pessoas ({horario_limpo}):** {zonas_texto.get(horario_limpo, '')}")
    
    with col_lista:
        st.subheader("🎯 Recomendações para Você")
        
        # Mostrar contexto
        if clima_limpo == "Chuva":
            st.warning("🌧️ Dia chuvoso — mostrando apenas locais cobertos")
        
        if df_recomendados.empty:
            st.info("Nenhum local encontrado para este contexto. Tente mudar o perfil ou condições.")
        else:
            for _, local in df_recomendados.iterrows():
                categoria = local["Categoria"]
                cat_class = f"cat-{categoria.lower().replace(' ', '-')}"
                
                st.markdown(
                    f"""
                    <div class="local-card">
                        <span class="categoria-badge {cat_class}">{categoria}</span>
                        <span style="color: #64748b; font-size: 0.8rem;">{'$' * int(local['Preco_Medio'])}</span>
                        <h4 style="margin: 0.5rem 0 0.25rem 0; color: #0f172a;">{local['Nome']}</h4>
                        <p style="margin: 0; font-size: 0.85rem; color: #64748b;">
                            {local.get('Descricao', '')}
                        </p>
                        <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #94a3b8;">
                            📍 {local['Tipo']} • ⏰ Melhor: {local['Horario_Pico']}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
        # Estatísticas
        st.divider()
        st.subheader("📊 Estatísticas")
        
        col1, col2 = st.columns(2)
        with col1:
            total_indoor = len(df_todos[df_todos["Tipo"] == "Indoor"])
            st.metric("Locais Cobertos", total_indoor)
        with col2:
            total_outdoor = len(df_todos[df_todos["Tipo"] == "Outdoor"])
            st.metric("Ao Ar Livre", total_outdoor)
        
        # Distribuição por categoria
        st.markdown("**Por Categoria:**")
        for cat in df_todos["Categoria"].unique():
            count = len(df_todos[df_todos["Categoria"] == cat])
            st.caption(f"• {cat}: {count} locais")

    # Menu de navegação
    render_sidebar_navegacao(app_atual=8)

    # Rodapé
    render_rodape(
        titulo_app="🗺️ PoA-Insight Explorer",
        subtitulo="Turismo inteligente em Porto Alegre com recomendações contextuais",
        tecnologias="Folium + Streamlit-Folium + Geopy + Streamlit"
    )


if __name__ == "__main__":
    render_app()
