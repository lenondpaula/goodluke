# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Dashboard de Monitoramento de Reputação de Marca - TechNova
Aplicação Streamlit para visualização da análise de sentimentos
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Monitor de Reputação - TechNova",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stMetric > div {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados():
    """Carrega os dados classificados do CSV."""
    caminho = 'data/comentarios_classificados.csv'
    
    if not os.path.exists(caminho):
        st.error(f"❌ Arquivo '{caminho}' não encontrado!")
        st.info("Execute primeiro:\n1. `python src/gerador_dados.py`\n2. `python src/analise_motor.py`")
        return None
    
    df = pd.read_csv(caminho)
    df['data'] = pd.to_datetime(df['data'])
    return df

def criar_kpis(df_filtrado: pd.DataFrame):
    """Cria os KPIs no topo do dashboard."""
    total = len(df_filtrado)
    
    if total == 0:
        st.warning("Nenhum dado encontrado com os filtros selecionados.")
        return
    
    positivos = len(df_filtrado[df_filtrado['classificacao'] == 'Positivo'])
    negativos = len(df_filtrado[df_filtrado['classificacao'] == 'Negativo'])
    neutros = len(df_filtrado[df_filtrado['classificacao'] == 'Neutro'])
    
    pct_positivos = (positivos / total) * 100
    pct_negativos = (negativos / total) * 100
    pct_neutros = (neutros / total) * 100
    
    polaridade_media = df_filtrado['polaridade'].mean()
    
    # Layout de KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📊 Total de Menções",
            value=f"{total:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="✅ Positivos",
            value=f"{pct_positivos:.1f}%",
            delta=f"{positivos} menções"
        )
    
    with col3:
        st.metric(
            label="❌ Negativos",
            value=f"{pct_negativos:.1f}%",
            delta=f"{negativos} menções",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="➖ Neutros",
            value=f"{pct_neutros:.1f}%",
            delta=f"{neutros} menções"
        )
    
    with col5:
        # Indicador de saúde da marca
        if polaridade_media > 0.1:
            emoji = "😊"
            status = "Saudável"
        elif polaridade_media < -0.1:
            emoji = "😟"
            status = "Atenção"
        else:
            status = "Estável"
            emoji = "😐"
        
        st.metric(
            label=f"{emoji} Saúde da Marca",
            value=status,
            delta=f"Polaridade: {polaridade_media:.2f}"
        )

def grafico_evolucao_sentimento(df_filtrado: pd.DataFrame):
    """Cria gráfico de linhas da evolução do sentimento médio por dia."""
    # Agrupa por data
    df_diario = df_filtrado.groupby(df_filtrado['data'].dt.date).agg({
        'polaridade': 'mean',
        'texto': 'count'
    }).reset_index()
    df_diario.columns = ['data', 'polaridade_media', 'quantidade']
    
    # Cria gráfico
    fig = go.Figure()
    
    # Linha de polaridade
    fig.add_trace(go.Scatter(
        x=df_diario['data'],
        y=df_diario['polaridade_media'],
        mode='lines+markers',
        name='Polaridade Média',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8),
        hovertemplate='Data: %{x}<br>Polaridade: %{y:.3f}<extra></extra>'
    ))
    
    # Linha de referência (zero)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Áreas coloridas
    fig.add_hrect(y0=0, y1=1, fillcolor="green", opacity=0.05, line_width=0)
    fig.add_hrect(y0=-1, y1=0, fillcolor="red", opacity=0.05, line_width=0)
    
    fig.update_layout(
        title='📈 Evolução do Sentimento Médio por Dia',
        xaxis_title='Data',
        yaxis_title='Polaridade Média',
        yaxis=dict(range=[-1, 1]),
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig

def grafico_pizza_sentimentos(df_filtrado: pd.DataFrame):
    """Cria gráfico de pizza com distribuição de sentimentos."""
    contagem = df_filtrado['classificacao'].value_counts()
    
    cores = {
        'Positivo': '#2ecc71',
        'Negativo': '#e74c3c',
        'Neutro': '#95a5a6'
    }
    
    fig = px.pie(
        values=contagem.values,
        names=contagem.index,
        color=contagem.index,
        color_discrete_map=cores,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}: %{value} menções<br>(%{percent})<extra></extra>'
    )
    
    fig.update_layout(
        title='🥧 Distribuição de Sentimentos',
        showlegend=True,
        height=400
    )
    
    return fig

def grafico_por_plataforma(df_filtrado: pd.DataFrame):
    """Cria gráfico de barras por plataforma."""
    df_plat = df_filtrado.groupby(['plataforma', 'classificacao']).size().reset_index(name='count')
    
    cores = {
        'Positivo': '#2ecc71',
        'Negativo': '#e74c3c',
        'Neutro': '#95a5a6'
    }
    
    fig = px.bar(
        df_plat,
        x='plataforma',
        y='count',
        color='classificacao',
        color_discrete_map=cores,
        barmode='group'
    )
    
    fig.update_layout(
        title='📱 Sentimentos por Plataforma',
        xaxis_title='Plataforma',
        yaxis_title='Quantidade',
        template='plotly_white',
        height=400
    )
    
    return fig

def tabela_comentarios(df_filtrado: pd.DataFrame):
    """Exibe tabela de comentários ordenados por likes."""
    df_exibir = df_filtrado[['data', 'plataforma', 'usuario', 'texto', 'classificacao', 'polaridade', 'likes']].copy()
    df_exibir = df_exibir.sort_values('likes', ascending=False)
    
    # Formata data
    df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y %H:%M')
    
    # Adiciona emoji de classificação
    emoji_map = {'Positivo': '✅', 'Negativo': '❌', 'Neutro': '➖'}
    df_exibir['classificacao'] = df_exibir['classificacao'].map(lambda x: f"{emoji_map.get(x, '')} {x}")
    
    # Renomeia colunas
    df_exibir.columns = ['Data', 'Plataforma', 'Usuário', 'Comentário', 'Sentimento', 'Polaridade', 'Likes']
    
    return df_exibir

def main():
    """Função principal do dashboard."""
    
    # Header
    st.markdown('<p class="main-header">📊 Monitor de Reputação de Marca</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">TechNova - Análise de Sentimentos em Tempo Real</p>', unsafe_allow_html=True)
    
    # Carrega dados
    df = carregar_dados()
    
    if df is None:
        return
    
    # Sidebar com filtros
    st.sidebar.header("🎛️ Filtros")
    
    # Filtro de plataforma
    plataformas = ['Todas'] + list(df['plataforma'].unique())
    plataforma_selecionada = st.sidebar.selectbox(
        "📱 Plataforma",
        plataformas
    )
    
    # Filtro de classificação
    classificacoes = ['Todas'] + list(df['classificacao'].unique())
    classificacao_selecionada = st.sidebar.selectbox(
        "🎭 Classificação de Sentimento",
        classificacoes
    )
    
    # Filtro de período
    st.sidebar.subheader("📅 Período")
    data_min = df['data'].min().date()
    data_max = df['data'].max().date()
    
    data_inicio = st.sidebar.date_input(
        "Data Inicial",
        value=data_min,
        min_value=data_min,
        max_value=data_max
    )
    
    data_fim = st.sidebar.date_input(
        "Data Final",
        value=data_max,
        min_value=data_min,
        max_value=data_max
    )
    
    # Aplica filtros
    df_filtrado = df.copy()
    
    if plataforma_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['plataforma'] == plataforma_selecionada]
    
    if classificacao_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['classificacao'] == classificacao_selecionada]
    
    df_filtrado = df_filtrado[
        (df_filtrado['data'].dt.date >= data_inicio) &
        (df_filtrado['data'].dt.date <= data_fim)
    ]
    
    # Info na sidebar
    st.sidebar.markdown("---")
    st.sidebar.info(f"📊 Exibindo **{len(df_filtrado):,}** de **{len(df):,}** menções")
    
    # KPIs
    st.markdown("---")
    criar_kpis(df_filtrado)
    
    # Gráficos
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_evolucao = grafico_evolucao_sentimento(df_filtrado)
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    with col2:
        fig_pizza = grafico_pizza_sentimentos(df_filtrado)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    # Gráfico por plataforma
    st.markdown("---")
    fig_plataforma = grafico_por_plataforma(df_filtrado)
    st.plotly_chart(fig_plataforma, use_container_width=True)
    
    # Tabela de comentários
    st.markdown("---")
    st.subheader("🔥 Comentários em Destaque (por Likes)")
    
    df_tabela = tabela_comentarios(df_filtrado)
    
    # Número de linhas a exibir
    n_linhas = st.slider("Número de comentários a exibir:", 5, 50, 20)
    
    st.dataframe(
        df_tabela.head(n_linhas),
        use_container_width=True,
        hide_index=True
    )
    
    # Download dos dados
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download dados filtrados (CSV)",
            data=csv,
            file_name=f"analise_sentimentos_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        st.info("💡 **Dica:** Use os filtros na barra lateral para refinar sua análise.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #888;'>"
        "🚀 Powered by TechNova Analytics | Análise de Sentimentos com TextBlob & Streamlit"
        "</p>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
