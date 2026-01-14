# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Visual-On-Demand — Marketplace Visual de Fotógrafos
Interface Streamlit para match visual inteligente
'O Shazam para encontrar o fotógrafo perfeito'
"""

import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

# Configuração de paths
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
ASSETS_DIR = BASE_DIR / "assets"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from motor_match import (  # noqa: E402
    analisar_estilo_imagem,
    encontrar_fotografos,
    obter_insights_estilo,
    carregar_fotografos,
)
from shared.components import (  # noqa: E402
    SHARED_SIDEBAR_CSS,
    render_sidebar_navegacao,
    render_rodape,
    render_instrucoes_uso,
)

# ============================================================================
# ESTILOS CSS
# ============================================================================

CUSTOM_CSS = """
<style>
    :root {
        --primary: #0f172a;
        --accent: #8b5cf6;
        --accent-light: #a78bfa;
        --success: #22c55e;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #1e1b4b;
        --bg-card: #312e81;
        --text-light: #e2e8f0;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--bg-dark) 0%, var(--accent) 100%);
        padding: 2.5rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        color: var(--text-light);
        font-size: 1.2rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    .upload-zone {
        background: linear-gradient(145deg, #f8fafc 0%, #e2e8f0 100%);
        border: 3px dashed var(--accent);
        border-radius: 1.5rem;
        padding: 3rem 2rem;
        text-align: center;
        margin: 2rem 0;
        transition: all 0.3s ease;
    }
    
    .upload-zone:hover {
        border-color: var(--accent-light);
        transform: translateY(-2px);
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.15);
    }
    
    .photographer-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid var(--accent);
        transition: all 0.3s ease;
    }
    
    .photographer-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.15);
    }
    
    .match-badge {
        background: linear-gradient(135deg, var(--success) 0%, #16a34a 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 2rem;
        font-weight: 700;
        font-size: 1.1rem;
        display: inline-block;
    }
    
    .match-badge.medium {
        background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
    }
    
    .price-tag {
        background: var(--primary);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .style-insight {
        background: linear-gradient(145deg, #faf5ff 0%, #ede9fe 100%);
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-left: 4px solid var(--accent);
    }
    
    .stat-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stat-card h3 {
        font-size: 2rem;
        color: var(--accent);
        margin: 0;
    }
    
    .stat-card p {
        color: #64748b;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
    }
    
    .success-banner {
        background: linear-gradient(135deg, var(--success) 0%, #16a34a 100%);
        color: white;
        padding: 2rem;
        border-radius: 1rem;
        text-align: center;
        margin: 2rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .filter-section {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1rem 0;
    }
    
    .loading-text {
        font-size: 1.1rem;
        color: var(--accent);
        font-weight: 500;
    }
</style>
"""

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_match_class(score: float) -> str:
    """Retorna a classe CSS baseada no score."""
    return "" if score >= 85 else "medium"


def format_ajustes(ajustes: list) -> str:
    """Formata os ajustes de preço para exibição."""
    if not ajustes:
        return "Preço padrão"
    return " | ".join([f"{nome}: {valor}" for nome, valor in ajustes])


def simular_analise_ia():
    """Simula o processo de análise de IA com feedback visual."""
    etapas = [
        ("🔍 Detectando elementos visuais...", 0.8),
        ("🎨 Analisando paleta de cores...", 0.7),
        ("💡 Avaliando iluminação e contraste...", 0.6),
        ("🧠 Processando características com IA...", 0.9),
        ("✨ Identificando estilo visual...", 0.5),
    ]
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (texto, delay) in enumerate(etapas):
        status_text.markdown(f"<p class='loading-text'>{texto}</p>", unsafe_allow_html=True)
        progress_bar.progress((i + 1) / len(etapas))
        time.sleep(delay)
    
    status_text.empty()
    progress_bar.empty()


# ============================================================================
# COMPONENTES DE UI
# ============================================================================

def render_header():
    """Renderiza o cabeçalho principal."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("""
        <div class='main-header'>
            <h1>📸 Visual-On-Demand</h1>
            <p>Encontre o olhar certo para o seu evento</p>
        </div>
    """, unsafe_allow_html=True)


def render_estatisticas():
    """Renderiza cards com estatísticas do marketplace."""
    try:
        df = carregar_fotografos()
        total = len(df)
        disponiveis = df["Disponivel"].sum()
        preco_medio = df["Preco_Hora"].mean()
        avaliacao_media = df["Avaliacao"].mean()
    except Exception:
        total, disponiveis, preco_medio, avaliacao_media = 50, 38, 300, 4.5
    
    cols = st.columns(4)
    
    stats = [
        ("📷", f"{total}", "Fotógrafos"),
        ("✅", f"{int(disponiveis)}", "Disponíveis"),
        ("💰", f"R$ {preco_medio:.0f}", "Preço Médio/h"),
        ("⭐", f"{avaliacao_media:.1f}", "Avaliação Média"),
    ]
    
    for col, (emoji, valor, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
                <div class='stat-card'>
                    <h3>{emoji} {valor}</h3>
                    <p>{label}</p>
                </div>
            """, unsafe_allow_html=True)


def render_insight_estilo(estilo: str, confianca: float, caracteristicas: dict):
    """Renderiza o insight do estilo detectado."""
    insight = obter_insights_estilo(estilo)
    
    st.markdown(f"""
        <div class='style-insight'>
            <h3>{insight['emoji']} Estilo Detectado: {insight['titulo']}</h3>
            <p><strong>Confiança da IA:</strong> {confianca * 100:.0f}%</p>
            <p>{insight['descricao']}</p>
            <p><strong>💡 Dica:</strong> {insight['dica']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Mostrar características extraídas
    with st.expander("🔬 Ver Análise Técnica da Imagem"):
        cols = st.columns(4)
        for i, (carac, valor) in enumerate(caracteristicas.items()):
            with cols[i % 4]:
                st.metric(carac, f"{valor:.0%}")


def render_fotografo_card(fotografo: pd.Series, rank: int):
    """Renderiza o card de um fotógrafo."""
    match_class = get_match_class(fotografo["Match_Score"])
    
    st.markdown(f"""
        <div class='photographer-card'>
            <div style='display: flex; justify-content: space-between; align-items: start;'>
                <div>
                    <h3 style='margin: 0; color: #1e293b;'>
                        #{rank} {fotografo['Nome']}
                    </h3>
                    <p style='color: #64748b; margin: 0.3rem 0;'>
                        {fotografo['Especialidade']} • {fotografo['Estilo_Dominante'].replace('_', ' ')}
                    </p>
                    <p style='margin: 0.3rem 0;'>
                        📍 {fotografo['Cidade']} • 📷 {fotografo['Equipamento']}
                    </p>
                    <p style='margin: 0.3rem 0;'>
                        ⭐ {fotografo['Avaliacao']} • 📂 {fotografo['Projetos_Concluidos']} projetos
                    </p>
                </div>
                <div style='text-align: right;'>
                    <span class='match-badge {match_class}'>{fotografo['Match_Score']:.0f}% Match</span>
                    <br><br>
                    <span class='price-tag'>R$ {fotografo['Preco_Dinamico']:.0f}/h</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_filtros() -> dict:
    """Renderiza a seção de filtros e retorna os valores."""
    with st.expander("🎛️ Filtros Avançados", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            orcamento = st.slider(
                "💰 Orçamento Máximo (R$/h)",
                min_value=100,
                max_value=600,
                value=500,
                step=50
            )
        
        with col2:
            data_evento = st.date_input(
                "📅 Data do Evento",
                value=datetime.now() + timedelta(days=14),
                min_value=datetime.now()
            )
        
        with col3:
            especialidades = [
                "Todas", "Casamentos", "Corporativo", "Moda", 
                "Produtos", "Retratos", "Eventos"
            ]
            especialidade = st.selectbox("🎯 Especialidade", especialidades)
        
        return {
            "orcamento": orcamento,
            "data_evento": datetime.combine(data_evento, datetime.min.time()),
            "especialidade": None if especialidade == "Todas" else especialidade
        }


def render_contratacao(fotografo_nome: str):
    """Renderiza a mensagem de contratação bem-sucedida."""
    st.markdown(f"""
        <div class='success-banner'>
            <h2>🎉 Solicitação Enviada!</h2>
            <p>Sua proposta foi enviada para <strong>{fotografo_nome}</strong></p>
            <p>Tempo médio de resposta: 2-4 horas</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.balloons()


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def render_app():
    """Função principal do dashboard Visual-On-Demand."""
    
    # Configuração da página
    st.set_page_config(
        page_title="Visual-On-Demand | Marketplace de Fotógrafos",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    # Inicializar estado
    if "contratado" not in st.session_state:
        st.session_state.contratado = None
    if "resultados" not in st.session_state:
        st.session_state.resultados = None
    if "estilo_detectado" not in st.session_state:
        st.session_state.estilo_detectado = None
    
    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Envie uma foto de inspiração (Pinterest, Instagram)",
            "A IA analisa cores, luz e atmosfera",
            "Receba fotógrafos com portfólio similar",
        ],
        ferramentas_sidebar=[
            "**Upload**: Arraste uma imagem de referência",
            "**Orçamento**: Defina seu limite de preço",
            "**Data**: Selecione a data do evento",
            "**Especialidade**: Filtre por tipo de fotografia",
        ]
    )
    
    # Header
    render_header()
    
    # Estatísticas
    render_estatisticas()
    
    st.markdown("---")
    
    # ========================================================================
    # SEÇÃO DE UPLOAD
    # ========================================================================
    
    st.markdown("### 🎨 Passo 1: Envie sua Foto de Inspiração")
    st.markdown("""
        <p style='color: #64748b; margin-bottom: 1rem;'>
        Suba uma foto do Pinterest, Instagram ou qualquer imagem que represente 
        o estilo visual que você sonha para seu evento. Nossa IA vai analisar as 
        cores, iluminação e atmosfera para encontrar o fotógrafo perfeito.
        </p>
    """, unsafe_allow_html=True)
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Arraste sua foto de referência aqui",
        type=["jpg", "jpeg", "png", "webp"],
        help="Formatos aceitos: JPG, PNG, WEBP. Tamanho máximo: 10MB"
    )
    
    # Filtros
    filtros = render_filtros()
    
    # ========================================================================
    # PROCESSAMENTO DA IMAGEM
    # ========================================================================
    
    if uploaded_file is not None:
        # Mostrar preview da imagem
        col_img, col_analise = st.columns([1, 2])
        
        with col_img:
            st.markdown("#### 📷 Sua Inspiração")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)
        
        with col_analise:
            st.markdown("#### 🤖 Análise de IA")
            
            # Resetar estado se nova imagem
            if st.button("🔍 Analisar Estilo Visual", type="primary", use_container_width=True):
                st.session_state.contratado = None
                
                # Simular análise
                simular_analise_ia()
                
                # Análise real
                uploaded_file.seek(0)  # Reset file pointer
                estilo, caracteristicas, confianca = analisar_estilo_imagem(uploaded_file)
                
                st.session_state.estilo_detectado = {
                    "estilo": estilo,
                    "caracteristicas": caracteristicas,
                    "confianca": confianca
                }
                
                # Buscar fotógrafos
                resultados = encontrar_fotografos(
                    estilo_desejado=estilo,
                    orcamento_max=filtros["orcamento"],
                    data_evento=filtros["data_evento"],
                    especialidade=filtros["especialidade"],
                    top_n=5
                )
                
                st.session_state.resultados = resultados
        
        # ====================================================================
        # RESULTADOS
        # ====================================================================
        
        if st.session_state.estilo_detectado:
            info = st.session_state.estilo_detectado
            
            render_insight_estilo(
                info["estilo"],
                info["confianca"],
                info["caracteristicas"]
            )
        
        if st.session_state.resultados is not None:
            resultados = st.session_state.resultados
            
            st.markdown("---")
            st.markdown("### 🏆 Fotógrafos Recomendados para Você")
            
            if len(resultados) == 0:
                st.warning(
                    "Nenhum fotógrafo encontrado com os filtros selecionados. "
                    "Tente aumentar o orçamento ou remover alguns filtros."
                )
            else:
                # Mostrar ajustes de preço se houver
                ajustes = resultados.iloc[0]["Ajustes_Preco"]
                if ajustes:
                    st.info(f"💡 **Precificação Dinâmica Ativa:** {format_ajustes(ajustes)}")
                
                # Cards dos fotógrafos
                for i, (_, fotografo) in enumerate(resultados.iterrows()):
                    col_card, col_btn = st.columns([4, 1])
                    
                    with col_card:
                        render_fotografo_card(fotografo, i + 1)
                    
                    with col_btn:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        if st.button(
                            "💼 Contratar",
                            key=f"contratar_{fotografo['ID']}",
                            use_container_width=True
                        ):
                            st.session_state.contratado = fotografo["Nome"]
                
                # Mensagem de contratação
                if st.session_state.contratado:
                    render_contratacao(st.session_state.contratado)
    
    else:
        # Seção de exemplo quando não há upload
        st.markdown("---")
        st.markdown("### 💡 Como Funciona?")
        
        cols = st.columns(3)
        
        passos = [
            ("1️⃣", "Envie uma Foto", "Suba uma imagem que represente o estilo que você ama"),
            ("2️⃣", "IA Analisa", "Nossa IA detecta cores, luz e atmosfera da imagem"),
            ("3️⃣", "Match Perfeito", "Encontramos fotógrafos com portfólio similar"),
        ]
        
        for col, (num, titulo, desc) in zip(cols, passos):
            with col:
                st.markdown(f"""
                    <div class='stat-card'>
                        <h2>{num}</h2>
                        <h4>{titulo}</h4>
                        <p>{desc}</p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Estilos disponíveis
        st.markdown("---")
        st.markdown("### 🎨 Estilos que Reconhecemos")
        
        estilos_info = [
            ("🌑", "Dark & Moody", "Cinematográfico, dramático, sombras profundas"),
            ("☀️", "Bright & Airy", "Luminoso, leve, tons pastéis"),
            ("⚫", "Preto & Branco", "Clássico, atemporal, foco em emoções"),
            ("🌈", "Cores Vibrantes", "Energético, saturado, alegre"),
        ]
        
        cols = st.columns(4)
        for col, (emoji, nome, desc) in zip(cols, estilos_info):
            with col:
                st.markdown(f"""
                    <div class='stat-card'>
                        <h2>{emoji}</h2>
                        <h4>{nome}</h4>
                        <p style='font-size: 0.85rem;'>{desc}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Menu de navegação
    render_sidebar_navegacao(app_atual=9)

    # Footer
    render_rodape(
        titulo_app="📸 Visual-On-Demand",
        subtitulo="Conectando talentos visuais a momentos únicos",
        tecnologias="Análise de Imagem + Match por IA + Streamlit"
    )


# Ponto de entrada direto
if __name__ == "__main__":
    render_app()
