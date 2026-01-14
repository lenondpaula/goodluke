# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Burger-Flow Intelligence - Dashboard de Gestão
Interface Streamlit para análise de estoque e engenharia de menu
"""

from pathlib import Path
import sys

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"

# Importa componentes compartilhados
sys.path.insert(0, str(PROJECT_ROOT))
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
    max-width: 1200px;
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
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: box-shadow 0.2s;
}
.kpi-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.kpi-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary);
}
.kpi-label {
    font-size: 0.85rem;
    color: var(--secondary);
    margin-top: 0.25rem;
}
.bcg-estrela { color: #d97706; font-weight: 600; }
.bcg-oportunidade { color: #1d4ed8; font-weight: 600; }
.bcg-vaca { color: #16a34a; font-weight: 600; }
.bcg-cao { color: #dc2626; font-weight: 600; }
.info-box {
    background: #f1f5f9;
    border-left: 4px solid #3b82f6;
    padding: 1rem 1.25rem;
    border-radius: 6px;
    margin-bottom: 1.5rem;
}
</style>
"""


@st.cache_data(show_spinner=False)
def carregar_dados():
    """Carrega todos os datasets necessários."""
    dados = {}
    
    # Vendas históricas
    vendas_path = DATA_DIR / "vendas_burger.csv"
    if vendas_path.exists():
        dados["vendas"] = pd.read_csv(vendas_path)
        dados["vendas"]["data"] = pd.to_datetime(dados["vendas"]["data"])
    
    # Performance do menu
    menu_path = DATA_DIR / "menu_performance.csv"
    if menu_path.exists():
        dados["menu"] = pd.read_csv(menu_path)
    
    # Previsão de estoque
    previsao_path = DATA_DIR / "previsao_estoque.csv"
    if previsao_path.exists():
        dados["previsao"] = pd.read_csv(previsao_path)
        dados["previsao"]["data"] = pd.to_datetime(dados["previsao"]["data"])
    
    # Necessidade de insumos
    insumos_path = DATA_DIR / "necessidade_insumos.csv"
    if insumos_path.exists():
        dados["insumos"] = pd.read_csv(insumos_path)
    
    return dados


def criar_grafico_bcg(df_menu: pd.DataFrame, ajuste_preco: float = 0) -> go.Figure:
    """
    Cria gráfico de dispersão BCG (Matriz de Engenharia de Menu).
    
    Eixo X: Volume de Vendas
    Eixo Y: Margem de Lucro (%)
    """
    df = df_menu.copy()
    
    # Aplicar ajuste de preço na margem
    if ajuste_preco != 0:
        df["Preco_Ajustado"] = df["Preco_Venda"] * (1 + ajuste_preco / 100)
        df["Margem_Ajustada"] = ((df["Preco_Ajustado"] - df["Custo_Producao"]) / df["Preco_Ajustado"] * 100).round(1)
    else:
        df["Margem_Ajustada"] = df["Margem_Percentual"]
    
    # Medianas para quadrantes
    mediana_volume = df["Volume_Vendas"].median()
    mediana_margem = df["Margem_Ajustada"].median()
    
    # Cores por classificação (cores mais escuras para melhor contraste)
    cores_bcg = {
        "⭐ Estrela": "#d97706",
        "🎯 Oportunidade": "#1d4ed8",
        "🐄 Vaca Leiteira": "#16a34a",
        "🐕 Cão/Retirar": "#dc2626",
    }
    
    # Reclassificar com margem ajustada
    def classificar(row):
        alto_volume = row["Volume_Vendas"] >= mediana_volume
        alta_margem = row["Margem_Ajustada"] >= mediana_margem
        
        if alta_margem and alto_volume:
            return "⭐ Estrela"
        elif alta_margem and not alto_volume:
            return "🎯 Oportunidade"
        elif not alta_margem and alto_volume:
            return "🐄 Vaca Leiteira"
        else:
            return "🐕 Cão/Retirar"
    
    df["Classificacao"] = df.apply(classificar, axis=1)
    
    # Criar figura
    fig = go.Figure()
    
    # Adicionar quadrantes como shapes
    max_volume = df["Volume_Vendas"].max() * 1.1
    max_margem = df["Margem_Ajustada"].max() * 1.1
    
    # Quadrante Estrela (superior direito)
    fig.add_shape(
        type="rect", x0=mediana_volume, x1=max_volume, y0=mediana_margem, y1=max_margem,
        fillcolor="rgba(245, 158, 11, 0.1)", line=dict(width=0),
    )
    
    # Quadrante Oportunidade (superior esquerdo)
    fig.add_shape(
        type="rect", x0=0, x1=mediana_volume, y0=mediana_margem, y1=max_margem,
        fillcolor="rgba(59, 130, 246, 0.1)", line=dict(width=0),
    )
    
    # Quadrante Vaca Leiteira (inferior direito)
    fig.add_shape(
        type="rect", x0=mediana_volume, x1=max_volume, y0=0, y1=mediana_margem,
        fillcolor="rgba(34, 197, 94, 0.1)", line=dict(width=0),
    )
    
    # Quadrante Cão (inferior esquerdo)
    fig.add_shape(
        type="rect", x0=0, x1=mediana_volume, y0=0, y1=mediana_margem,
        fillcolor="rgba(239, 68, 68, 0.1)", line=dict(width=0),
    )
    
    # Linhas de mediana
    fig.add_hline(y=mediana_margem, line_dash="dash", line_color="#64748b", opacity=0.5)
    fig.add_vline(x=mediana_volume, line_dash="dash", line_color="#64748b", opacity=0.5)
    
    # Pontos por classificação
    for classe, cor in cores_bcg.items():
        df_classe = df[df["Classificacao"] == classe]
        if not df_classe.empty:
            fig.add_trace(go.Scatter(
                x=df_classe["Volume_Vendas"],
                y=df_classe["Margem_Ajustada"],
                mode="markers+text",
                name=classe,
                text=df_classe["Item"],
                textposition="top center",
                marker=dict(size=15, color=cor, line=dict(width=2, color="white")),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Volume: %{x:,} un<br>"
                    "Margem: %{y:.1f}%<br>"
                    "<extra></extra>"
                ),
            ))
    
    # Anotações dos quadrantes
    fig.add_annotation(x=max_volume * 0.85, y=max_margem * 0.95, text="⭐ ESTRELAS", showarrow=False, font=dict(size=12, color="#92400e"))
    fig.add_annotation(x=mediana_volume * 0.15, y=max_margem * 0.95, text="🎯 OPORTUNIDADES", showarrow=False, font=dict(size=12, color="#1e40af"))
    fig.add_annotation(x=max_volume * 0.85, y=mediana_margem * 0.15, text="🐄 VACAS LEITEIRAS", showarrow=False, font=dict(size=12, color="#166534"))
    fig.add_annotation(x=mediana_volume * 0.15, y=mediana_margem * 0.15, text="🐕 CÃES", showarrow=False, font=dict(size=12, color="#991b1b"))
    
    fig.update_layout(
        title=dict(text="Matriz de Engenharia de Menu (BCG Adaptada)", font=dict(size=18)),
        xaxis_title="Volume de Vendas (un/mês)",
        yaxis_title="Margem de Lucro (%)",
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
    )
    
    return fig, df


def criar_grafico_previsao(df_previsao: pd.DataFrame) -> go.Figure:
    """Cria gráfico de previsão de demanda por produto."""
    fig = go.Figure()
    
    cores = {"Burger Clássico": "#d97706", "Burger Gourmet": "#1d4ed8", "Batata Frita": "#16a34a"}
    
    for produto in df_previsao["produto"].unique():
        df_prod = df_previsao[df_previsao["produto"] == produto]
        
        # Área de confiança
        fig.add_trace(go.Scatter(
            x=pd.concat([df_prod["data"], df_prod["data"][::-1]]),
            y=pd.concat([df_prod["limite_superior"], df_prod["limite_inferior"][::-1]]),
            fill="toself",
            fillcolor=f"rgba({','.join(str(int(cores[produto][i:i+2], 16)) for i in (1, 3, 5))}, 0.2)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=False,
            name=f"{produto} (IC 95%)",
        ))
        
        # Linha principal
        fig.add_trace(go.Scatter(
            x=df_prod["data"],
            y=df_prod["previsao"],
            mode="lines+markers",
            name=produto,
            line=dict(color=cores.get(produto, "#64748b"), width=2),
            marker=dict(size=8),
        ))
    
    fig.update_layout(
        title=dict(text="Previsão de Demanda - Próximos 7 Dias", font=dict(size=18)),
        xaxis_title="Data",
        yaxis_title="Vendas Previstas (un)",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        plot_bgcolor="white",
    )
    
    return fig


def render_app():
    """Renderiza o dashboard principal."""
    st.set_page_config(
        page_title="Burger-Flow Intelligence",
        page_icon="🍔",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    st.title("🍔 Burger-Flow Intelligence")
    st.markdown("Dashboard de gestão inteligente para hamburguerias")
    
    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Analise a previsão de demanda para 7 dias",
            "Use a Matriz BCG para otimizar o menu",
            "Simule ajustes de preço e veja o impacto",
        ],
        ferramentas_sidebar=[
            "**Ajuste Preço**: Simule aumento/redução no menu",
            "**Abas**: Navegue entre Previsão, BCG e Histórico",
        ]
    )
    
    # Descrição do sistema
    st.markdown(
        """
        <div class="info-box">
            <strong>O que é?</strong><br>
            Sistema de inteligência operacional que combina <em>Análise Preditiva</em> para gestão de estoque
            e <em>Engenharia de Menu</em> para otimização do cardápio.<br><br>
            <strong>Funcionalidades</strong><br>
            • <b>Previsão de Demanda:</b> Estima vendas dos próximos 7 dias com Prophet<br>
            • <b>Sugestão de Compras:</b> Calcula insumos necessários para a semana<br>
            • <b>Matriz BCG:</b> Classifica itens do menu em Estrelas, Oportunidades, Vacas e Cães
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Carregar dados
    dados = carregar_dados()
    
    if not dados:
        st.warning("⚠️ Dados não encontrados. Execute os scripts de geração primeiro:")
        st.code("cd projeto-burger-flow\npython src/gerar_dados_burger.py\npython src/previsao_estoque.py")
        return
    
    # Sidebar com controles
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        ajuste_preco = st.slider(
            "📈 Simular Ajuste de Preço (%)",
            min_value=-20,
            max_value=30,
            value=0,
            step=5,
            help="Simula o efeito de um aumento ou desconto no preço sobre a margem",
        )
        
        st.divider()
        st.markdown("### 📊 Legendas BCG")
        st.markdown("⭐ **Estrela** — Alta margem, alto volume")
        st.markdown("🎯 **Oportunidade** — Alta margem, baixo volume")
        st.markdown("🐄 **Vaca Leiteira** — Baixa margem, alto volume")
        st.markdown("🐕 **Cão** — Baixa margem, baixo volume")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 1: Gestão de Estoque
    # ─────────────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📦 Gestão de Estoque", "📋 Engenharia de Menu", "📈 Análise Histórica"])
    
    with tab1:
        st.subheader("📦 Sugestão de Pedido para a Semana")
        
        if "insumos" in dados and "previsao" in dados:
            col1, col2 = st.columns([1, 1.5])
            
            with col1:
                st.markdown("### 🥩 Insumos Necessários")
                df_insumos = dados["insumos"]
                
                # Estilizar tabela
                st.dataframe(
                    df_insumos.style.format({"Quantidade": "{:.1f}"}),
                    use_container_width=True,
                    hide_index=True,
                )
                
                # KPIs de previsão
                df_prev = dados["previsao"]
                total_burgers = df_prev[df_prev["produto"].str.contains("Burger")]["previsao"].sum()
                total_batatas = df_prev[df_prev["produto"] == "Batata Frita"]["previsao"].sum()
                
                st.markdown("### 📊 Resumo Semanal")
                kpi1, kpi2 = st.columns(2)
                with kpi1:
                    st.metric("🍔 Total Burgers", f"{total_burgers:,}")
                with kpi2:
                    st.metric("🍟 Total Batatas", f"{total_batatas:,}")
            
            with col2:
                st.markdown("### 🔮 Previsão de Demanda")
                fig_prev = criar_grafico_previsao(dados["previsao"])
                st.plotly_chart(fig_prev, use_container_width=True)
        else:
            st.info("Execute `python src/previsao_estoque.py` para gerar previsões.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 2: Engenharia de Menu
    # ─────────────────────────────────────────────────────────────────────────
    with tab2:
        st.subheader("📋 Engenharia de Menu — Matriz BCG")
        
        if "menu" in dados:
            df_menu = dados["menu"]
            
            # Mostrar ajuste de preço
            if ajuste_preco != 0:
                st.info(f"📊 Simulando ajuste de **{ajuste_preco:+d}%** no preço de venda")
            
            # Gráfico BCG
            fig_bcg, df_classificado = criar_grafico_bcg(df_menu, ajuste_preco)
            st.plotly_chart(fig_bcg, use_container_width=True)
            
            # Tabela detalhada
            st.markdown("### 📝 Detalhamento por Item")
            
            # Preparar DataFrame para exibição
            df_display = df_classificado[["Item", "Custo_Producao", "Preco_Venda", "Volume_Vendas", "Margem_Ajustada", "Lucro_Total", "Classificacao"]].copy()
            df_display.columns = ["Item", "Custo (R$)", "Preço (R$)", "Volume (un)", "Margem (%)", "Lucro Total (R$)", "Classificação"]
            
            st.dataframe(
                df_display.style.format({
                    "Custo (R$)": "R$ {:.2f}",
                    "Preço (R$)": "R$ {:.2f}",
                    "Volume (un)": "{:,}",
                    "Margem (%)": "{:.1f}%",
                    "Lucro Total (R$)": "R$ {:,.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )
            
            # Insights automáticos
            st.markdown("### 💡 Insights e Recomendações")
            
            estrelas = df_classificado[df_classificado["Classificacao"] == "⭐ Estrela"]["Item"].tolist()
            oportunidades = df_classificado[df_classificado["Classificacao"] == "🎯 Oportunidade"]["Item"].tolist()
            caes = df_classificado[df_classificado["Classificacao"] == "🐕 Cão/Retirar"]["Item"].tolist()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.success(f"⭐ **Manter destaque:** {', '.join(estrelas) if estrelas else 'Nenhum'}")
            with col2:
                st.info(f"🎯 **Investir em marketing:** {', '.join(oportunidades) if oportunidades else 'Nenhum'}")
            with col3:
                st.error(f"🐕 **Avaliar remoção:** {', '.join(caes) if caes else 'Nenhum'}")
        else:
            st.info("Execute `python src/gerar_dados_burger.py` para gerar dados do menu.")
    
    # ─────────────────────────────────────────────────────────────────────────
    # TAB 3: Análise Histórica
    # ─────────────────────────────────────────────────────────────────────────
    with tab3:
        st.subheader("📈 Análise de Vendas Históricas")
        
        if "vendas" in dados:
            df_vendas = dados["vendas"]
            
            # Vendas por dia da semana
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📅 Vendas por Dia da Semana")
                df_dia = df_vendas.groupby("dia_semana")["vendas"].mean().reset_index()
                ordem_dias = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                df_dia["dia_semana"] = pd.Categorical(df_dia["dia_semana"], categories=ordem_dias, ordered=True)
                df_dia = df_dia.sort_values("dia_semana")
                
                fig_dia = px.bar(
                    df_dia, x="dia_semana", y="vendas",
                    color="vendas", color_continuous_scale=["#93c5fd", "#1d4ed8", "#1e3a8a"],
                )
                fig_dia.update_layout(
                    xaxis_title="Dia da Semana",
                    yaxis_title="Média de Vendas",
                    showlegend=False,
                    height=350,
                )
                st.plotly_chart(fig_dia, use_container_width=True)
            
            with col2:
                st.markdown("### 🍔 Vendas por Produto")
                df_prod = df_vendas.groupby("produto")["vendas"].sum().reset_index()
                
                fig_prod = px.pie(
                    df_prod, values="vendas", names="produto",
                    color_discrete_sequence=["#d97706", "#1d4ed8", "#16a34a"],
                    hole=0.4,
                )
                fig_prod.update_layout(height=350)
                st.plotly_chart(fig_prod, use_container_width=True)
            
            # Série temporal
            st.markdown("### 📊 Evolução de Vendas (Últimos 90 Dias)")
            df_recente = df_vendas[df_vendas["data"] >= df_vendas["data"].max() - pd.Timedelta(days=90)]
            df_agrupado = df_recente.groupby(["data", "produto"])["vendas"].sum().reset_index()
            
            fig_serie = px.line(
                df_agrupado, x="data", y="vendas", color="produto",
                color_discrete_map={"Burger Clássico": "#d97706", "Burger Gourmet": "#1d4ed8", "Batata Frita": "#16a34a"},
            )
            fig_serie.update_layout(
                xaxis_title="Data",
                yaxis_title="Vendas",
                height=400,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig_serie, use_container_width=True)
        else:
            st.info("Execute `python src/gerar_dados_burger.py` para gerar histórico de vendas.")

    # Menu de navegação
    render_sidebar_navegacao(app_atual=7)

    # Rodapé
    render_rodape(
        titulo_app="🍔 Burger-Flow Intelligence",
        subtitulo="Gestão inteligente de estoque e engenharia de menu",
        tecnologias="Prophet + Matriz BCG + Plotly + Streamlit"
    )


if __name__ == "__main__":
    render_app()
