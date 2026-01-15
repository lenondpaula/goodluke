# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
GIG-Master AI - Dashboard de Planejamento de Turnês
Interface principal com visualizações interativas e plano de marketing
"""

import json
import sys
from datetime import datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração de paths
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"

# Adicionar src ao path para imports
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from shared.components import (  # noqa: E402
    SHARED_SIDEBAR_CSS,
    render_sidebar_header,
    render_sidebar_footer,
    render_rodape,
    render_instrucoes_uso,
)

# CSS corporativo consistente com o hub - adaptável a tema claro/escuro
CUSTOM_CSS = """
<style>
/* Variáveis que se adaptam ao tema do Streamlit */
:root {
    --accent: #8b5cf6;
    --accent-2: #a855f7;
    --success: #22c55e;
    --warning: #f59e0b;
    --danger: #ef4444;
}

/* Override apenas para elementos customizados */
.stApp {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #8b5cf6 0%, #6366f1 50%, #3b82f6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.sub-header {
    opacity: 0.7;
    font-size: 1.1rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(139, 92, 246, 0.05);
    border: 2px solid rgba(139, 92, 246, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.metric-card:hover {
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.3);
}

.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent);
}

.metric-label {
    font-size: 0.9rem;
    opacity: 0.7;
    margin-top: 0.5rem;
}

.city-card {
    background: rgba(139, 92, 246, 0.05);
    border: 1px solid rgba(139, 92, 246, 0.2);
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(10px);
}

.city-card:hover {
    border-color: var(--accent);
}

.phase-tag {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

.phase-aquecimento { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border: 1px solid rgba(59, 130, 246, 0.3); }
.phase-prevenda { background: rgba(168, 85, 247, 0.15); color: #a855f7; border: 1px solid rgba(168, 85, 247, 0.3); }
.phase-venda { background: rgba(34, 197, 94, 0.15); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.3); }
.phase-engajamento { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
.phase-ultima { background: rgba(239, 68, 68, 0.15); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.phase-pos { background: rgba(148, 163, 184, 0.15); color: #64748b; border: 1px solid rgba(148, 163, 184, 0.3); }

.timeline-item {
    border-left: 3px solid var(--accent);
    padding-left: 1rem;
    margin-bottom: 1.5rem;
}

.timeline-item strong {
    font-weight: 600;
}

.timeline-item li {
    margin-bottom: 0.3rem;
}

.export-btn {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent-2) 100%);
    color: white;
    border: none;
    padding: 0.8rem 2rem;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.export-btn:hover {
    transform: scale(1.02);
    box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.region-badge {
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    border: 1px solid;
}

.region-sudeste { background: rgba(59, 130, 246, 0.15); color: #3b82f6; border-color: rgba(59, 130, 246, 0.3); }
.region-sul { background: rgba(34, 197, 94, 0.15); color: #22c55e; border-color: rgba(34, 197, 94, 0.3); }
.region-nordeste { background: rgba(245, 158, 11, 0.15); color: #f59e0b; border-color: rgba(245, 158, 11, 0.3); }
.region-norte { background: rgba(168, 85, 247, 0.15); color: #a855f7; border-color: rgba(168, 85, 247, 0.3); }
.region-centro-oeste { background: rgba(239, 68, 68, 0.15); color: #ef4444; border-color: rgba(239, 68, 68, 0.3); }
</style>
"""


@st.cache_data(show_spinner=False)
def carregar_plano_turne() -> pd.DataFrame:
    """Carrega o plano de turnê otimizado."""
    csv_path = DATA_DIR / "plano_turne.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


@st.cache_data(show_spinner=False)
def carregar_mercado() -> pd.DataFrame:
    """Carrega dados de mercado."""
    csv_path = DATA_DIR / "mercado_shows.csv"
    if csv_path.exists():
        return pd.read_csv(csv_path)
    return None


@st.cache_data(show_spinner=False)
def carregar_planos_marketing() -> list:
    """Carrega planos de marketing."""
    json_path = DATA_DIR / "planos_marketing.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def gerar_dados_se_necessario():
    """Gera dados automaticamente se não existirem."""
    from gerar_mercado import main as gerar_mercado
    from motor_logistica import main as gerar_plano
    
    mercado_path = DATA_DIR / "mercado_shows.csv"
    plano_path = DATA_DIR / "plano_turne.csv"
    
    if not mercado_path.exists():
        with st.spinner("🎸 Gerando dados de mercado..."):
            gerar_mercado()
    
    if not plano_path.exists():
        with st.spinner("🗺️ Otimizando rota da turnê..."):
            gerar_plano()


def criar_grafico_timeline(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de timeline/Gantt da turnê."""
    ano = datetime.now().year + 1
    
    # Criar dados para o Gantt
    dados_gantt = []
    cores_regiao = {
        "Sudeste": "#3b82f6",
        "Sul": "#22c55e",
        "Nordeste": "#f59e0b",
        "Norte": "#a855f7",
        "Centro-Oeste": "#ef4444",
    }
    
    meses_num = {
        "Janeiro": 1, "Fevereiro": 2, "Março": 3, "Abril": 4,
        "Maio": 5, "Junho": 6, "Julho": 7, "Agosto": 8,
        "Setembro": 9, "Outubro": 10, "Novembro": 11, "Dezembro": 12
    }
    
    for _, row in df.iterrows():
        mes = meses_num.get(row["Mês"], 1)
        data_inicio = datetime(ano, mes, 1)
        data_fim = datetime(ano, mes, 28)  # Simplificado
        
        dados_gantt.append({
            "Task": f"{row['Mês']}: {row['Cidade']}",
            "Start": data_inicio,
            "Finish": data_fim,
            "Região": row["Região"],
            "Lucro": row["Lucro Potencial (R$)"],
            "Score": row["Score"],
        })
    
    df_gantt = pd.DataFrame(dados_gantt)
    
    fig = px.timeline(
        df_gantt,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="Região",
        color_discrete_map=cores_regiao,
        hover_data=["Lucro", "Score"],
    )
    
    fig.update_layout(
        title="📅 Cronograma Anual da Turnê",
        xaxis_title="",
        yaxis_title="",
        height=500,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
    )
    
    fig.update_yaxes(autorange="reversed")
    
    return fig


def criar_grafico_lucro(df: pd.DataFrame) -> go.Figure:
    """Cria gráfico de barras de lucro potencial."""
    cores_regiao = {
        "Sudeste": "#3b82f6",
        "Sul": "#22c55e",
        "Nordeste": "#f59e0b",
        "Norte": "#a855f7",
        "Centro-Oeste": "#ef4444",
    }
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["Cidade"],
        y=df["Lucro Potencial (R$)"],
        marker_color=[cores_regiao.get(r, "#8b5cf6") for r in df["Região"]],
        text=[f"R$ {v:,.0f}" for v in df["Lucro Potencial (R$)"]],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Lucro: R$ %{y:,.2f}<extra></extra>",
    ))
    
    fig.update_layout(
        title="💰 Potencial de Lucro por Cidade",
        xaxis_title="",
        yaxis_title="Lucro Potencial (R$)",
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        xaxis=dict(tickangle=45),
    )
    
    return fig


def criar_grafico_mapa(df: pd.DataFrame, df_mercado: pd.DataFrame) -> go.Figure:
    """Cria mapa com a rota da turnê."""
    # Extrair cidade e estado do plano
    cidades_turne = [c.split("/")[0] for c in df["Cidade"]]
    
    # Filtrar mercado para cidades da turnê
    df_rota = df_mercado[df_mercado["cidade"].isin(cidades_turne)].copy()
    
    # Ordenar pela sequência da turnê
    ordem = {cidade: i for i, cidade in enumerate(cidades_turne)}
    df_rota["ordem"] = df_rota["cidade"].map(ordem)
    df_rota = df_rota.sort_values("ordem")
    
    fig = go.Figure()
    
    # Linha conectando as cidades
    fig.add_trace(go.Scattergeo(
        lon=df_rota["longitude"],
        lat=df_rota["latitude"],
        mode="lines",
        line=dict(width=2, color="#8b5cf6"),
        name="Rota",
        hoverinfo="skip",
    ))
    
    # Pontos das cidades
    cores_regiao = {
        "Sudeste": "#3b82f6",
        "Sul": "#22c55e",
        "Nordeste": "#f59e0b",
        "Norte": "#a855f7",
        "Centro-Oeste": "#ef4444",
    }
    
    for regiao, cor in cores_regiao.items():
        df_regiao = df_rota[df_rota["regiao"] == regiao]
        if len(df_regiao) > 0:
            fig.add_trace(go.Scattergeo(
                lon=df_regiao["longitude"],
                lat=df_regiao["latitude"],
                mode="markers+text",
                marker=dict(size=15, color=cor, symbol="circle"),
                text=[f"{i+1}" for i in df_regiao["ordem"]],
                textposition="middle center",
                textfont=dict(size=10, color="white"),
                name=regiao,
                hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
                customdata=list(zip(df_regiao["cidade"], df_regiao["estado"])),
            ))
    
    fig.update_geos(
        resolution=50,
        showcoastlines=True,
        coastlinecolor="#475569",
        showland=True,
        landcolor="#1e293b",
        showocean=True,
        oceancolor="#0f172a",
        showcountries=True,
        countrycolor="#475569",
        showframe=False,
        lonaxis_range=[-75, -30],
        lataxis_range=[-35, 5],
    )
    
    fig.update_layout(
        title="🗺️ Mapa da Rota da Turnê",
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    
    return fig


def exibir_plano_marketing(planos: list, cidade_selecionada: str):
    """Exibe o plano de marketing para a cidade selecionada."""
    # Encontrar plano da cidade
    plano = None
    for p in planos:
        if p["cidade"] == cidade_selecionada:
            plano = p
            break
    
    if not plano:
        st.warning("Plano de marketing não encontrado para esta cidade.")
        return
    
    st.markdown(f"### 📢 Plano de Marketing: {plano['cidade']}")
    st.markdown(f"**Data do Show:** {plano['data_show']} ({plano['mes_nome']})")
    
    # Cores das fases
    fase_cores = {
        "Aquecimento": "phase-aquecimento",
        "Pré-Venda": "phase-prevenda",
        "Venda Geral": "phase-venda",
        "Engajamento": "phase-engajamento",
        "Última Chamada": "phase-ultima",
        "Pós-Show": "phase-pos",
    }
    
    for item in plano["cronograma"]:
        fase = item["fase"]
        classe = fase_cores.get(fase, "phase-aquecimento")
        
        st.markdown(f"""
        <div class="timeline-item">
            <span class="phase-tag {classe}">{fase}</span>
            <strong>Início: {item['data_inicio']}</strong> (Investimento: {item['investimento_sugerido']})
            <br><br>
            <strong>Atividades:</strong>
            <ul>
                {''.join(f'<li>{a}</li>' for a in item['atividades'])}
            </ul>
            <strong>Canais:</strong> {', '.join(item['canais'])}
        </div>
        """, unsafe_allow_html=True)


def gerar_pdf_plano(df: pd.DataFrame, planos: list) -> bytes:
    """Gera PDF do plano anual (simulado como HTML para download)."""
    # Criar HTML do relatório
    ano = datetime.now().year + 1
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Plano de Turnê {ano} - GIG-Master AI</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; }}
            h1 {{ color: #8b5cf6; }}
            h2 {{ color: #6366f1; border-bottom: 2px solid #8b5cf6; padding-bottom: 10px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            th {{ background: #8b5cf6; color: white; }}
            tr:nth-child(even) {{ background: #f9fafb; }}
            .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #8b5cf6; }}
            .metric-label {{ font-size: 12px; color: #666; }}
            .fase {{ margin: 20px 0; padding: 15px; background: #f3f4f6; border-radius: 8px; }}
            .fase h4 {{ margin-top: 0; color: #6366f1; }}
        </style>
    </head>
    <body>
        <h1>🎸 GIG-Master AI - Plano de Turnê {ano}</h1>
        <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        
        <h2>📊 Resumo Executivo</h2>
        <div class="metric">
            <div class="metric-value">R$ {df['Lucro Potencial (R$)'].sum():,.2f}</div>
            <div class="metric-label">Lucro Total Estimado</div>
        </div>
        <div class="metric">
            <div class="metric-value">{len(df)}</div>
            <div class="metric-label">Shows Planejados</div>
        </div>
        <div class="metric">
            <div class="metric-value">{df['Distância do Anterior (km)'].sum():,.0f} km</div>
            <div class="metric-label">Distância Total</div>
        </div>
        <div class="metric">
            <div class="metric-value">{df['ROI (%)'].mean():.1f}%</div>
            <div class="metric-label">ROI Médio</div>
        </div>
        
        <h2>📅 Cronograma da Turnê</h2>
        <table>
            <tr>
                <th>Mês</th>
                <th>Cidade</th>
                <th>Região</th>
                <th>Lucro Potencial</th>
                <th>ROI</th>
                <th>Score</th>
            </tr>
    """
    
    for _, row in df.iterrows():
        html += f"""
            <tr>
                <td>{row['Mês']}</td>
                <td>{row['Cidade']}</td>
                <td>{row['Região']}</td>
                <td>R$ {row['Lucro Potencial (R$)']:,.2f}</td>
                <td>{row['ROI (%)']:.1f}%</td>
                <td>{row['Score']:.1f}</td>
            </tr>
        """
    
    html += "</table>"
    
    # Adicionar planos de marketing
    html += "<h2>📢 Planos de Marketing por Cidade</h2>"
    
    for plano in planos[:3]:  # Apenas os 3 primeiros para não ficar muito longo
        html += f"""
        <div class="fase">
            <h4>{plano['mes_nome']}: {plano['cidade']} (Show: {plano['data_show']})</h4>
        """
        for item in plano["cronograma"]:
            html += f"""
            <p><strong>{item['fase']}</strong> - Início: {item['data_inicio']} ({item['investimento_sugerido']})<br>
            Atividades: {', '.join(item['atividades'][:2])}<br>
            Canais: {', '.join(item['canais'])}</p>
            """
        html += "</div>"
    
    html += """
        <p style="margin-top: 40px; color: #666; font-size: 12px;">
            Este relatório foi gerado automaticamente pelo GIG-Master AI.<br>
            Os valores são estimativas baseadas em dados de mercado simulados.
        </p>
    </body>
    </html>
    """
    
    return html.encode("utf-8")


def render_app():
    """Função principal do dashboard."""
    st.set_page_config(
        page_title="GIG-Master AI",
        page_icon="🎸",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    # Header
    st.markdown('<p class="main-header">🎸 GIG-Master AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Planejamento Inteligente de Turnês Musicais • Análise Preditiva + Marketing</p>', unsafe_allow_html=True)
    
    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Explore o cronograma otimizado de shows",
            "Analise o ROI por cidade e região",
            "Baixe o plano de marketing integrado",
        ],
        ferramentas_sidebar=[
            "**Cidade**: Selecione para ver plano de marketing",
            "**Exportar HTML**: Plano anual completo",
            "**Exportar CSV**: Cronograma para Excel",
        ]
    )
    
    # Gerar dados se necessário
    try:
        gerar_dados_se_necessario()
    except Exception as e:
        st.error(f"Erro ao gerar dados: {e}")
        st.info("Execute manualmente: `python src/gerar_mercado.py && python src/motor_logistica.py`")
        return
    
    # Carregar dados
    df_plano = carregar_plano_turne()
    df_mercado = carregar_mercado()
    planos_marketing = carregar_planos_marketing()
    
    if df_plano is None or df_mercado is None:
        st.error("Dados não encontrados. Por favor, gere os dados primeiro.")
        return
    
    # ── Sidebar Header (Home + Menu Aplicações) ─────────────────────────────────
    render_sidebar_header()

    # Conteúdo específico do app na sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Configurações")
        
        # Seletor de cidade para marketing
        cidades_turne = [c.split("/")[0] for c in df_plano["Cidade"]]
        cidade_selecionada = st.selectbox(
            "📍 Cidade para Plano de Marketing",
            cidades_turne,
            index=0,
        )
        
        st.markdown("---")
        
        # Botão de exportar
        st.markdown("### 📥 Exportar")
        if planos_marketing:
            html_content = gerar_pdf_plano(df_plano, planos_marketing)
            st.download_button(
                label="📄 Baixar Plano Anual (HTML)",
                data=html_content,
                file_name=f"plano_turne_{datetime.now().year + 1}.html",
                mime="text/html",
            )
        
        # Exportar CSV
        csv_buffer = df_plano.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📊 Baixar Cronograma (CSV)",
            data=csv_buffer,
            file_name=f"cronograma_turne_{datetime.now().year + 1}.csv",
            mime="text/csv",
        )
        
        st.markdown("---")
        st.markdown("### 📈 Estatísticas")
        st.metric("Lucro Total", f"R$ {df_plano['Lucro Potencial (R$)'].sum():,.0f}")
        st.metric("Distância Total", f"{df_plano['Distância do Anterior (km)'].sum():,.0f} km")
        st.metric("ROI Médio", f"{df_plano['ROI (%)'].mean():.1f}%")

    # ── Sidebar Footer (Contato + Copyright) ────────────────────────────────────
    render_sidebar_footer()
    
    # KPIs principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(df_plano)}</div>
            <div class="metric-label">Shows Planejados</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        lucro_total = df_plano["Lucro Potencial (R$)"].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">R$ {lucro_total/1_000_000:.2f}M</div>
            <div class="metric-label">Lucro Total Estimado</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        distancia_total = df_plano["Distância do Anterior (km)"].sum()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{distancia_total:,.0f} km</div>
            <div class="metric-label">Distância Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        roi_medio = df_plano["ROI (%)"].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{roi_medio:.1f}%</div>
            <div class="metric-label">ROI Médio</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Timeline", "💰 Lucro", "🗺️ Mapa", "📢 Marketing"])
    
    with tab1:
        fig_timeline = criar_grafico_timeline(df_plano)
        st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("### 📋 Detalhes do Cronograma")
        st.dataframe(
            df_plano.style.format({
                "Lucro Potencial (R$)": "R$ {:,.2f}",
                "Preço Ingresso (R$)": "R$ {:,.2f}",
                "Distância do Anterior (km)": "{:,.0f} km",
                "Distância Acumulada (km)": "{:,.0f} km",
                "Lucro Acumulado (R$)": "R$ {:,.2f}",
                "Score": "{:.1f}",
                "ROI (%)": "{:.1f}%",
                "Capacidade Venue": "{:,.0f}",
            }),
            use_container_width=True,
            hide_index=True,
        )
    
    with tab2:
        fig_lucro = criar_grafico_lucro(df_plano)
        st.plotly_chart(fig_lucro, use_container_width=True)
        
        # Análise de ROI
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏆 Top 5 por ROI")
            top_roi = df_plano.nlargest(5, "ROI (%)")[["Cidade", "ROI (%)", "Lucro Potencial (R$)"]]
            st.dataframe(
                top_roi.style.format({
                    "ROI (%)": "{:.1f}%",
                    "Lucro Potencial (R$)": "R$ {:,.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )
        
        with col2:
            st.markdown("### 📊 Distribuição por Região")
            lucro_regiao = df_plano.groupby("Região")["Lucro Potencial (R$)"].sum().reset_index()
            fig_pizza = px.pie(
                lucro_regiao,
                values="Lucro Potencial (R$)",
                names="Região",
                color="Região",
                color_discrete_map={
                    "Sudeste": "#3b82f6",
                    "Sul": "#22c55e",
                    "Nordeste": "#f59e0b",
                    "Norte": "#a855f7",
                    "Centro-Oeste": "#ef4444",
                },
            )
            fig_pizza.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc"),
            )
            st.plotly_chart(fig_pizza, use_container_width=True)
    
    with tab3:
        if df_mercado is not None:
            fig_mapa = criar_grafico_mapa(df_plano, df_mercado)
            st.plotly_chart(fig_mapa, use_container_width=True)
            
            # Legenda da rota
            st.markdown("### 🔢 Sequência da Rota")
            rota_cols = st.columns(6)
            for i, (_, row) in enumerate(df_plano.iterrows()):
                with rota_cols[i % 6]:
                    regiao_classe = f"region-{row['Região'].lower().replace('-', '-')}"
                    st.markdown(f"""
                    <div class="city-card">
                        <strong>{i+1}. {row['Cidade']}</strong><br>
                        <span class="region-badge {regiao_classe}">{row['Região']}</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab4:
        if planos_marketing:
            exibir_plano_marketing(planos_marketing, cidade_selecionada)
        else:
            st.warning("Planos de marketing não encontrados.")

    # Footer
    render_rodape(
        titulo_app="🎸 GIG-Master AI",
        subtitulo="Otimização de turnês musicais com algoritmos inteligentes",
        tecnologias="Otimização Greedy + Plotly + Streamlit"
    )


if __name__ == "__main__":
    render_app()
