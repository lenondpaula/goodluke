"""
Dashboard do Oráculo de Vendas - BI Preditivo
Painel interativo que mostra vendas históricas e previsão para próximos 30 dias
"""

from pathlib import Path
import pickle
from datetime import datetime, timedelta

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "vendas_historico.csv"
MODEL_PATH = BASE_DIR / "models" / "prophet_model.pkl"

# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista (padrão do Hub)
# ────────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
:root {
    --primary: #0f172a;
    --secondary: #334155;
    --accent: #3b82f6;
    --success: #22c55e;
    --danger: #ef4444;
    --warning: #f59e0b;
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
.kpi-delta {
    font-size: 0.8rem;
    margin-top: 0.25rem;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    display: inline-block;
}
.kpi-delta.positive {
    background: #dcfce7;
    color: #166534;
}
.kpi-delta.negative {
    background: #fee2e2;
    color: #991b1b;
}
.status-card {
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: 1.1rem;
    font-weight: 600;
    margin-top: 1rem;
}
.status-ok {
    background: linear-gradient(135deg, #d1fae5, #a7f3d0);
    color: #065f46;
    border: 1px solid #34d399;
}
.status-warning {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    color: #92400e;
    border: 1px solid #fbbf24;
}
</style>
"""


@st.cache_data(show_spinner=False)
def carregar_dados() -> pd.DataFrame:
    """Carrega histórico de vendas."""
    if not DATA_PATH.exists():
        return None
    df = pd.read_csv(DATA_PATH)
    df['ds'] = pd.to_datetime(df['ds'])
    return df


@st.cache_resource(show_spinner=False)
def carregar_modelo():
    """Carrega modelo Prophet treinado."""
    if not MODEL_PATH.exists():
        return None
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def gerar_previsao(modelo, dias_futuro: int = 30) -> pd.DataFrame:
    """Gera previsão para os próximos N dias."""
    futuro = modelo.make_future_dataframe(periods=dias_futuro)
    previsao = modelo.predict(futuro)
    return previsao


def calcular_kpis(df_historico: pd.DataFrame, df_previsao: pd.DataFrame, dias_futuro: int = 30):
    """Calcula KPIs de negócio."""
    
    # Previsão próximo mês
    previsao_futura = df_previsao.tail(dias_futuro)
    venda_prevista_mes = previsao_futura['yhat'].sum()
    
    # Mês anterior (últimos 30 dias do histórico)
    ultimos_30_dias = df_historico.tail(30)
    venda_mes_anterior = ultimos_30_dias['y'].sum()
    
    # Crescimento
    crescimento = ((venda_prevista_mes - venda_mes_anterior) / venda_mes_anterior) * 100
    
    # Média diária
    media_diaria_prevista = previsao_futura['yhat'].mean()
    media_diaria_historico = df_historico['y'].mean()
    
    # Intervalo de confiança
    venda_pessimista = previsao_futura['yhat_lower'].sum()
    venda_otimista = previsao_futura['yhat_upper'].sum()
    
    return {
        'venda_prevista_mes': venda_prevista_mes,
        'venda_mes_anterior': venda_mes_anterior,
        'crescimento_pct': crescimento,
        'media_diaria_prevista': media_diaria_prevista,
        'media_diaria_historico': media_diaria_historico,
        'venda_pessimista': venda_pessimista,
        'venda_otimista': venda_otimista,
    }


def criar_grafico_principal(df_historico: pd.DataFrame, df_previsao: pd.DataFrame, dias_futuro: int = 30):
    """Cria gráfico com histórico e previsão."""
    
    # Separa dados históricos e futuros na previsão
    data_corte = df_historico['ds'].max()
    
    fig = go.Figure()
    
    # Histórico real
    fig.add_trace(go.Scatter(
        x=df_historico['ds'],
        y=df_historico['y'],
        mode='lines',
        name='Vendas Reais',
        line=dict(color='#3b82f6', width=1.5),
        hovertemplate='Data: %{x}<br>Vendas: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Previsão (apenas período futuro)
    previsao_futura = df_previsao[df_previsao['ds'] > data_corte]
    
    # Intervalo de confiança (área sombreada)
    fig.add_trace(go.Scatter(
        x=pd.concat([previsao_futura['ds'], previsao_futura['ds'][::-1]]),
        y=pd.concat([previsao_futura['yhat_upper'], previsao_futura['yhat_lower'][::-1]]),
        fill='toself',
        fillcolor='rgba(34, 197, 94, 0.2)',
        line=dict(color='rgba(0,0,0,0)'),
        name='Intervalo de Confiança (95%)',
        hoverinfo='skip'
    ))
    
    # Linha de previsão
    fig.add_trace(go.Scatter(
        x=previsao_futura['ds'],
        y=previsao_futura['yhat'],
        mode='lines',
        name='Previsão',
        line=dict(color='#22c55e', width=2.5, dash='dash'),
        hovertemplate='Data: %{x}<br>Previsão: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Linha vertical separando histórico de previsão
    # Converte Timestamp para string ISO para compatibilidade com Plotly
    data_corte_str = data_corte.strftime('%Y-%m-%d')
    fig.add_shape(
        type="line",
        x0=data_corte_str,
        x1=data_corte_str,
        y0=0,
        y1=1,
        yref="paper",
        line=dict(color="#64748b", width=2, dash="dot"),
    )
    fig.add_annotation(
        x=data_corte_str,
        y=1.05,
        yref="paper",
        text="Hoje",
        showarrow=False,
        font=dict(color="#64748b", size=12),
    )
    
    fig.update_layout(
        title='📈 Vendas Históricas e Previsão para os Próximos 30 Dias',
        xaxis_title='Data',
        yaxis_title='Vendas (R$)',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        font=dict(family="Inter, Segoe UI, sans-serif"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def criar_grafico_componentes(modelo, df_previsao: pd.DataFrame):
    """Cria gráficos de decomposição da série temporal."""
    
    # Gráfico de tendência
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df_previsao['ds'],
        y=df_previsao['trend'],
        mode='lines',
        name='Tendência',
        line=dict(color='#8b5cf6', width=2)
    ))
    fig_trend.update_layout(
        title='📊 Tendência de Crescimento',
        xaxis_title='Data',
        yaxis_title='Tendência',
        template='plotly_white',
        height=350,
        font=dict(family="Inter, Segoe UI, sans-serif")
    )
    
    # Gráfico de sazonalidade semanal
    dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Calcula média por dia da semana
    df_previsao['dia_semana'] = df_previsao['ds'].dt.dayofweek
    semanal = df_previsao.groupby('dia_semana')['weekly'].mean().reset_index()
    
    fig_weekly = go.Figure()
    fig_weekly.add_trace(go.Bar(
        x=dias_semana,
        y=semanal['weekly'],
        marker_color=['#94a3b8' if i < 5 else '#22c55e' for i in range(7)],
        hovertemplate='%{x}: %{y:.2f}<extra></extra>'
    ))
    fig_weekly.update_layout(
        title='📅 Padrão Semanal de Vendas',
        xaxis_title='Dia da Semana',
        yaxis_title='Efeito nas Vendas',
        template='plotly_white',
        height=350,
        font=dict(family="Inter, Segoe UI, sans-serif")
    )
    
    return fig_trend, fig_weekly


def render_kpis(kpis: dict):
    """Renderiza os KPIs no topo do dashboard."""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta_class = "positive" if kpis['crescimento_pct'] >= 0 else "negative"
        delta_symbol = "↑" if kpis['crescimento_pct'] >= 0 else "↓"
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">R$ {kpis['venda_prevista_mes']:,.0f}</div>
                <div class="kpi-label">Venda Prevista (30 dias)</div>
                <div class="kpi-delta {delta_class}">{delta_symbol} {abs(kpis['crescimento_pct']):.1f}% vs mês anterior</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">R$ {kpis['venda_mes_anterior']:,.0f}</div>
                <div class="kpi-label">Vendas Mês Anterior</div>
                <div class="kpi-delta" style="background:#f1f5f9; color:#64748b;">Base de comparação</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value">R$ {kpis['media_diaria_prevista']:,.0f}</div>
                <div class="kpi-label">Média Diária Prevista</div>
                <div class="kpi-delta" style="background:#dbeafe; color:#1e40af;">Meta diária</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-value" style="font-size:1.2rem;">R$ {kpis['venda_pessimista']:,.0f}<br>a<br>R$ {kpis['venda_otimista']:,.0f}</div>
                <div class="kpi-label">Intervalo de Confiança (95%)</div>
            </div>
        """, unsafe_allow_html=True)


def render_app():
    """Função principal do dashboard - chamada pela página do hub."""
    
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    st.title("🔮 O Oráculo de Vendas")
    st.markdown("Previsão inteligente de vendas com análise de séries temporais (Prophet)")
    
    # Apresentação
    with st.container():
        st.markdown(
            """
            <div style="background:#f1f5f9; border-left:4px solid #8b5cf6; padding:1rem 1.25rem; border-radius:6px; margin-bottom:1.5rem;">
                <strong>O que é?</strong><br>
                Este painel utiliza o modelo <em>Prophet (Meta/Facebook)</em> para prever vendas futuras
                com base em padrões históricos, sazonalidade e tendências de mercado.<br><br>
                <strong>Aplicações</strong><br>
                • Planejamento de estoque e compras<br>
                • Projeção de fluxo de caixa<br>
                • Definição de metas de vendas baseadas em dados
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Carrega dados e modelo
    df_historico = carregar_dados()
    modelo = carregar_modelo()
    
    if df_historico is None or modelo is None:
        st.error("⚠️ Dados ou modelo não encontrados. Execute primeiro:")
        st.code("""
cd oraculo-vendas
python src/gerar_vendas.py      # Gera dados históricos
python src/treinar_oraculo.py   # Treina o modelo
        """)
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configurações")
        dias_previsao = st.slider("Dias de previsão", 7, 90, 30, 7)
        mostrar_componentes = st.checkbox("Mostrar decomposição", value=True)
        st.markdown("---")
        st.caption(f"📊 Dados: {len(df_historico):,} dias")
        st.caption(f"📅 Até: {df_historico['ds'].max().strftime('%d/%m/%Y')}")
    
    # Gera previsão
    with st.spinner("🔮 Consultando o Oráculo..."):
        df_previsao = gerar_previsao(modelo, dias_previsao)
    
    # Calcula e exibe KPIs
    kpis = calcular_kpis(df_historico, df_previsao, dias_previsao)
    st.markdown("---")
    render_kpis(kpis)
    
    # Status da previsão
    if kpis['crescimento_pct'] >= 5:
        st.markdown(
            '<div class="status-card status-ok">📈 TENDÊNCIA DE CRESCIMENTO DETECTADA</div>',
            unsafe_allow_html=True
        )
    elif kpis['crescimento_pct'] <= -5:
        st.markdown(
            '<div class="status-card status-warning">📉 ATENÇÃO: TENDÊNCIA DE QUEDA</div>',
            unsafe_allow_html=True
        )
    
    # Gráfico principal
    st.markdown("---")
    fig_principal = criar_grafico_principal(df_historico, df_previsao, dias_previsao)
    st.plotly_chart(fig_principal, use_container_width=True)
    
    # Componentes da série temporal
    if mostrar_componentes:
        st.markdown("---")
        st.subheader("🔍 Decomposição da Série Temporal")
        
        col1, col2 = st.columns(2)
        fig_trend, fig_weekly = criar_grafico_componentes(modelo, df_previsao)
        
        with col1:
            st.plotly_chart(fig_trend, use_container_width=True)
        
        with col2:
            st.plotly_chart(fig_weekly, use_container_width=True)
    
    # Download da previsão
    st.markdown("---")
    with st.expander("📥 Exportar Previsão"):
        previsao_export = df_previsao[df_previsao['ds'] > df_historico['ds'].max()][
            ['ds', 'yhat', 'yhat_lower', 'yhat_upper']
        ].copy()
        previsao_export.columns = ['Data', 'Previsão', 'Mínimo (95%)', 'Máximo (95%)']
        previsao_export['Data'] = previsao_export['Data'].dt.strftime('%Y-%m-%d')
        
        st.dataframe(previsao_export, use_container_width=True, hide_index=True)
        
        csv = previsao_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Download Previsão (CSV)",
            data=csv,
            file_name=f"previsao_vendas_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Rodapé
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#64748b; font-size:0.85rem;">
            Desenvolvido por <strong>Lenon de Paula</strong> · 
            <a href="mailto:lenondpaula@gmail.com" style="color:#3b82f6;">lenondpaula@gmail.com</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Permite execução direta para desenvolvimento
if __name__ == "__main__":
    st.set_page_config(
        page_title="Oráculo de Vendas",
        page_icon="🔮",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_app()
