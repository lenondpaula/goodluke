"""
Dashboard de Monitoramento de Reputação de Marca - TechNova
Aplicação Streamlit para visualização da análise de sentimentos
Integrado ao Hub de Criação
"""

from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import numpy as np

# Download NLTK data necessário para TextBlob
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

from textblob import TextBlob

# Caminhos do projeto - ajustado para raiz
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALISE_PATH = PROJECT_ROOT / "analise-sentimentos"
DATA_PATH = ANALISE_PATH / "data" / "comentarios_classificados.csv"

# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista (mesmo padrão do App 1)
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
    max-width: 1100px;
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
.status-card {
    border-radius: 12px;
    padding: 1.5rem 2rem;
    text-align: center;
    font-size: 1.25rem;
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
.status-danger {
    background: linear-gradient(135deg, #fee2e2, #fecaca);
    color: #991b1b;
    border: 1px solid #f87171;
}
.kpi-container {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    margin: 1.5rem 0;
}
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    flex: 1;
    transition: box-shadow 0.2s;
}
.kpi-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--primary);
}
.kpi-label {
    font-size: 0.85rem;
    color: var(--secondary);
    margin-top: 0.25rem;
}
.kpi-delta {
    font-size: 0.75rem;
    margin-top: 0.25rem;
}
.kpi-delta.positive { color: var(--success); }
.kpi-delta.negative { color: var(--danger); }
.kpi-delta.neutral { color: var(--secondary); }
</style>
"""

# Templates de comentários para geração de dados
ELOGIOS_SUPORTE = [
    "O suporte da TechNova é incrível! Resolveram meu problema em minutos 🙌",
    "Atendimento nota 10! A equipe da TechNova é muito prestativa",
    "Nunca vi suporte tão rápido. TechNova mandou bem demais!",
    "Parabéns @TechNova pelo atendimento excepcional! Super recomendo",
    "A TechNova tem o melhor suporte que já vi. Equipe 100%!",
    "Problema resolvido em 5 minutos! Obrigado TechNova 👏",
    "Adorei o atendimento da TechNova, muito profissionais!",
    "Suporte TechNova salvou meu dia! Muito obrigado! ❤️",
]

RECLAMACOES_BATERIA = [
    "A bateria do produto TechNova está durando muito pouco 😡",
    "Decepcionado com a bateria do TechNova, não dura nem 4 horas",
    "Bateria péssima! TechNova precisa melhorar urgente isso",
    "Terceira vez que reclamo da bateria e nada muda @TechNova",
    "Produto TechNova é bom, mas a bateria é uma vergonha",
    "Não comprem TechNova se precisam de bateria boa, frustrante",
    "Bateria descarrega do nada! TechNova precisa resolver isso",
    "Estou arrependido da compra, bateria TechNova é muito fraca",
]

DUVIDAS_PRECO = [
    "Alguém sabe se a TechNova vai fazer promoção na Black Friday?",
    "Qual o preço do modelo novo da TechNova?",
    "TechNova tem desconto pra estudante?",
    "Vale a pena pagar mais caro no TechNova Pro?",
    "Onde encontro TechNova mais barato?",
    "TechNova aceita parcelamento em quantas vezes?",
]

COMENTARIOS_GERAIS = [
    "Design do TechNova é muito bonito, adorei a cor!",
    "TechNova chegou antes do prazo, embalagem perfeita 📦",
    "Usando TechNova há 6 meses e estou satisfeito",
    "Qualidade do TechNova superou minhas expectativas!",
    "TechNova é bom mas poderia ser melhor no preço",
    "Recomendo TechNova pra quem busca qualidade",
    "Meu TechNova parou de funcionar depois de 1 ano 😢",
    "Tela do TechNova é linda, cores vibrantes!",
]

PLATAFORMAS = ['Twitter', 'Instagram', 'Facebook']
USUARIOS = ['@tech_lover', '@maria_silva', '@joao_dev', '@ana_tech', '@pedro_gamer', 
            '@julia_design', '@carlos_eng', '@fernanda_mkt', '@lucas_ti', '@patricia_ux']


def analisar_sentimento(texto: str):
    """Analisa o sentimento de um texto usando TextBlob."""
    try:
        blob = TextBlob(str(texto))
        polaridade = blob.sentiment.polarity
        
        if polaridade > 0.1:
            classificacao = 'Positivo'
        elif polaridade < -0.1:
            classificacao = 'Negativo'
        else:
            classificacao = 'Neutro'
            
        return polaridade, classificacao, blob.sentiment.subjectivity
    except Exception:
        return 0.0, 'Neutro', 0.5


@st.cache_data
def gerar_dados_sinteticos(n_comentarios: int = 500):
    """Gera dados sintéticos de comentários."""
    random.seed(42)
    np.random.seed(42)
    
    categorias = {
        'elogio': ELOGIOS_SUPORTE,
        'reclamacao': RECLAMACOES_BATERIA,
        'duvida': DUVIDAS_PRECO,
        'geral': COMENTARIOS_GERAIS
    }
    pesos_categorias = [0.25, 0.25, 0.20, 0.30]
    
    dados = []
    data_base = datetime.now()
    
    for _ in range(n_comentarios):
        categoria = random.choices(list(categorias.keys()), weights=pesos_categorias)[0]
        texto = random.choice(categorias[categoria])
        
        dias_atras = random.randint(0, 30)
        hora = random.randint(0, 23)
        minuto = random.randint(0, 59)
        data = data_base - timedelta(days=dias_atras, hours=hora, minutes=minuto)
        
        plataforma = random.choice(PLATAFORMAS)
        usuario = random.choice(USUARIOS)
        
        if categoria == 'reclamacao':
            likes = int(np.random.exponential(scale=150))
        elif categoria == 'elogio':
            likes = int(np.random.exponential(scale=80))
        else:
            likes = int(np.random.exponential(scale=40))
        
        polaridade, classificacao, subjetividade = analisar_sentimento(texto)
        
        dados.append({
            'data': data,
            'plataforma': plataforma,
            'usuario': usuario,
            'texto': texto,
            'likes': min(likes, 10000),
            'polaridade': polaridade,
            'classificacao': classificacao,
            'subjetividade': subjetividade
        })
    
    df = pd.DataFrame(dados)
    df = df.sort_values('data', ascending=False).reset_index(drop=True)
    
    return df


@st.cache_data
def carregar_dados():
    """Carrega os dados - do CSV se existir, senão gera em memória."""
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        df['data'] = pd.to_datetime(df['data'])
        return df
    else:
        # Gera dados em memória para Streamlit Cloud
        return gerar_dados_sinteticos(500)


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
    polaridade_media = df_filtrado['polaridade'].mean()
    
    # Determina saúde da marca
    if polaridade_media > 0.1:
        saude = "Saudável"
        saude_emoji = "😊"
    elif polaridade_media < -0.1:
        saude = "Atenção"
        saude_emoji = "😟"
    else:
        saude = "Estável"
        saude_emoji = "😐"
    
    # Layout de KPIs usando colunas do Streamlit
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="📊 Total de Menções",
            value=f"{total:,}"
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
            value=f"{neutros}",
            delta=f"{(neutros/total)*100:.1f}%"
        )
    
    with col5:
        st.metric(
            label=f"{saude_emoji} Saúde da Marca",
            value=saude,
            delta=f"Polaridade: {polaridade_media:.2f}"
        )


def grafico_evolucao_sentimento(df_filtrado: pd.DataFrame):
    """Cria gráfico de linhas da evolução do sentimento médio por dia."""
    df_diario = df_filtrado.groupby(df_filtrado['data'].dt.date).agg({
        'polaridade': 'mean',
        'texto': 'count'
    }).reset_index()
    df_diario.columns = ['data', 'polaridade_media', 'quantidade']
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_diario['data'],
        y=df_diario['polaridade_media'],
        mode='lines+markers',
        name='Polaridade Média',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8),
        hovertemplate='Data: %{x}<br>Polaridade: %{y:.3f}<extra></extra>'
    ))
    
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b", opacity=0.5)
    fig.add_hrect(y0=0, y1=1, fillcolor="#22c55e", opacity=0.05, line_width=0)
    fig.add_hrect(y0=-1, y1=0, fillcolor="#ef4444", opacity=0.05, line_width=0)
    
    fig.update_layout(
        title='📈 Evolução do Sentimento Médio por Dia',
        xaxis_title='Data',
        yaxis_title='Polaridade Média',
        yaxis=dict(range=[-1, 1]),
        hovermode='x unified',
        template='plotly_white',
        height=400,
        font=dict(family="Inter, Segoe UI, sans-serif")
    )
    
    return fig


def grafico_pizza_sentimentos(df_filtrado: pd.DataFrame):
    """Cria gráfico de pizza com distribuição de sentimentos."""
    contagem = df_filtrado['classificacao'].value_counts()
    
    cores = {
        'Positivo': '#22c55e',
        'Negativo': '#ef4444',
        'Neutro': '#94a3b8'
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
        height=400,
        font=dict(family="Inter, Segoe UI, sans-serif")
    )
    
    return fig


def grafico_por_plataforma(df_filtrado: pd.DataFrame):
    """Cria gráfico de barras por plataforma."""
    df_plat = df_filtrado.groupby(['plataforma', 'classificacao']).size().reset_index(name='count')
    
    cores = {
        'Positivo': '#22c55e',
        'Negativo': '#ef4444',
        'Neutro': '#94a3b8'
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
        height=400,
        font=dict(family="Inter, Segoe UI, sans-serif")
    )
    
    return fig


def tabela_comentarios(df_filtrado: pd.DataFrame):
    """Exibe tabela de comentários ordenados por likes."""
    df_exibir = df_filtrado[['data', 'plataforma', 'usuario', 'texto', 'classificacao', 'polaridade', 'likes']].copy()
    df_exibir = df_exibir.sort_values('likes', ascending=False)
    
    df_exibir['data'] = df_exibir['data'].dt.strftime('%d/%m/%Y %H:%M')
    
    emoji_map = {'Positivo': '✅', 'Negativo': '❌', 'Neutro': '➖'}
    df_exibir['classificacao'] = df_exibir['classificacao'].map(lambda x: f"{emoji_map.get(x, '')} {x}")
    
    df_exibir.columns = ['Data', 'Plataforma', 'Usuário', 'Comentário', 'Sentimento', 'Polaridade', 'Likes']
    
    return df_exibir


def render_saude_marca(polaridade_media: float):
    """Renderiza o indicador de saúde da marca."""
    if polaridade_media > 0.1:
        st.markdown(
            '<div class="status-card status-ok">😊 REPUTAÇÃO SAUDÁVEL</div>',
            unsafe_allow_html=True,
        )
    elif polaridade_media < -0.1:
        st.markdown(
            '<div class="status-card status-danger">😟 REPUTAÇÃO EM RISCO</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="status-card status-warning">😐 REPUTAÇÃO ESTÁVEL</div>',
            unsafe_allow_html=True,
        )


def layout():
    """Configura o layout da página."""
    st.set_page_config(
        page_title="Análise de Sentimentos - TechNova",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.title("📊 Monitor de Reputação de Marca")
    st.markdown("Análise de sentimentos em tempo real para a marca **TechNova**.")

    # Apresentação (mesmo estilo do App 1)
    with st.container():
        st.markdown(
            """
            <div style="background:#f1f5f9; border-left:4px solid #3b82f6; padding:1rem 1.25rem; border-radius:6px; margin-bottom:1.5rem;">
                <strong>O que é?</strong><br>
                Este painel utiliza <em>Processamento de Linguagem Natural (NLP)</em> para analisar 
                o sentimento de menções em redes sociais sobre a marca TechNova.<br><br>
                <strong>Aplicações</strong><br>
                • Monitoramento de reputação de marca em redes sociais<br>
                • Identificação de crises de imagem em tempo real<br>
                • Análise de feedback de clientes e tendências de opinião
            </div>
            """,
            unsafe_allow_html=True,
        )


def main():
    """Função principal do dashboard."""
    layout()
    
    # Carrega dados (gera automaticamente se não existir)
    df = carregar_dados()
    
    if df is None or len(df) == 0:
        st.error("❌ Não foi possível carregar os dados.")
        st.stop()
    
    # Sidebar com filtros
    with st.sidebar:
        st.header("🎛️ Filtros")
        
        # Filtro de plataforma
        plataformas = ['Todas'] + list(df['plataforma'].unique())
        plataforma_selecionada = st.selectbox(
            "📱 Plataforma",
            plataformas
        )
        
        # Filtro de classificação
        classificacoes = ['Todas'] + list(df['classificacao'].unique())
        classificacao_selecionada = st.selectbox(
            "🎭 Classificação",
            classificacoes
        )
        
        # Filtro de período
        st.subheader("📅 Período")
        data_min = df['data'].min().date()
        data_max = df['data'].max().date()
        
        data_inicio = st.date_input(
            "Data Inicial",
            value=data_min,
            min_value=data_min,
            max_value=data_max
        )
        
        data_fim = st.date_input(
            "Data Final",
            value=data_max,
            min_value=data_min,
            max_value=data_max
        )
        
        st.markdown("---")
        
        # Botão para regenerar dados
        if st.button("🔄 Regenerar Dados", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
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
    
    # Info de filtros aplicados
    st.caption(f"📊 Exibindo **{len(df_filtrado):,}** de **{len(df):,}** menções")
    
    # KPIs
    st.markdown("---")
    criar_kpis(df_filtrado)
    
    # Indicador de saúde da marca
    if len(df_filtrado) > 0:
        polaridade_media = df_filtrado['polaridade'].mean()
        render_saude_marca(polaridade_media)
    
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
    fig_plataforma = grafico_por_plataforma(df_filtrado)
    st.plotly_chart(fig_plataforma, use_container_width=True)
    
    # Tabela de comentários
    st.markdown("---")
    st.subheader("🔥 Comentários em Destaque")
    st.caption("Ordenados por número de likes (potencial de viralização)")
    
    df_tabela = tabela_comentarios(df_filtrado)
    
    n_linhas = st.slider("Número de comentários:", 5, 50, 15)
    
    st.dataframe(
        df_tabela.head(n_linhas),
        use_container_width=True,
        hide_index=True
    )
    
    # Download dos dados
    with st.expander("📥 Exportar Dados"):
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download dados filtrados (CSV)",
            data=csv,
            file_name=f"analise_sentimentos_{datetime.now().strftime('%Y%m%d')}.csv",
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


if __name__ == "__main__":
    main()
