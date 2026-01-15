import streamlit as st
import sys
from pathlib import Path

# Importa componentes compartilhados para sidebar padronizada
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from shared.components import APPS_DO_HUB  # noqa: E402

# Configuração da página
st.set_page_config(page_title="GoodLuke AI Hub", layout="wide", page_icon="🚀")

# CSS para sidebar + portfólio "Arrojado" com responsividade mobile
st.markdown("""
    <style>
        /* ============ SIDEBAR ESTILIZADA ============ */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0e1117 0%, #1a1a2e 100%);
        }
        
        section[data-testid="stSidebar"] * {
            color: #FAFAFA !important;
        }
        
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-weight: 600;
        }
        
        section[data-testid="stSidebar"] hr {
            border-color: #FF4B4B;
            opacity: 0.5;
        }
        
        /* Botões na sidebar */
        section[data-testid="stSidebar"] button {
            background: #FF4B4B !important;
            color: #FFFFFF !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }
        
        section[data-testid="stSidebar"] button:hover {
            background: #e63946 !important;
            transform: translateY(-1px);
        }
        
        section[data-testid="stSidebar"] button:disabled {
            background: #333 !important;
            color: #888 !important;
        }
        
        /* Expander na sidebar */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            background: #262730;
            border-radius: 8px;
            border-left: 3px solid #FF4B4B;
        }
        
        section[data-testid="stSidebar"] .streamlit-expanderHeader:hover {
            background: #31333F;
        }
        
        section[data-testid="stSidebar"] .streamlit-expanderContent {
            background: #1a1a2e;
            border-radius: 0 0 8px 8px;
        }
        
        /* Home button especial */
        section[data-testid="stSidebar"] .home-title {
            text-align: center;
            font-size: 1.5em;
            color: #FF4B4B !important;
            margin-bottom: 0.5em;
        }
        
        /* ============ MAIN CONTENT ============ */
        .main {
            background-color: #0e1117;
        }
        
        /* Responsividade geral */
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem !important;
                max-width: 100% !important;
            }
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #FF4B4B;
            color: white;
            font-size: 14px;
        }
        
        @media (max-width: 480px) {
            .stButton>button {
                height: 2.5em;
                font-size: 12px;
            }
        }
        
        .project-card {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF4B4B;
            margin-bottom: 20px;
            min-height: 280px;
            overflow: hidden;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
        }
        
        @media (max-width: 768px) {
            .project-card {
                padding: 15px;
                min-height: 260px;
                margin-bottom: 15px;
            }
        }
        
        @media (max-width: 480px) {
            .project-card {
                padding: 12px;
                min-height: 240px;
                margin-bottom: 10px;
            }
        }
        
        .project-title {
            color: #FF4B4B;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
            word-wrap: break-word;
            word-break: break-word;
        }
        
        @media (max-width: 768px) {
            .project-title {
                font-size: 18px;
                margin-bottom: 8px;
            }
        }
        
        @media (max-width: 480px) {
            .project-title {
                font-size: 15px;
                margin-bottom: 6px;
            }
        }
        
        .project-tag {
            font-size: 11px;
            background-color: #31333F;
            padding: 4px 8px;
            border-radius: 15px;
            color: #A3A8B4;
            display: inline-block;
            word-wrap: break-word;
            word-break: break-word;
        }
        
        @media (max-width: 480px) {
            .project-tag {
                font-size: 9px;
                padding: 3px 6px;
            }
        }
        
        .project-desc {
            color: #FAFAFA;
            font-size: 14px;
            flex-grow: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
        }
        
        @media (max-width: 768px) {
            .project-desc {
                font-size: 13px;
                -webkit-line-clamp: 2;
            }
        }
        
        @media (max-width: 480px) {
            .project-desc {
                font-size: 12px;
                -webkit-line-clamp: 2;
            }
        }
        
        .header-title {
            color: #FF4B4B;
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.2em;
            word-wrap: break-word;
        }
        
        @media (max-width: 768px) {
            .header-title {
                font-size: 2.2em;
            }
        }
        
        @media (max-width: 480px) {
            .header-title {
                font-size: 1.8em;
            }
        }
        
        .header-subtitle {
            color: #FFFFFF;
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 0.3em;
        }
        
        @media (max-width: 768px) {
            .header-subtitle {
                font-size: 1em;
            }
        }
        
        @media (max-width: 480px) {
            .header-subtitle {
                font-size: 0.85em;
            }
        }
        
        .contact-links {
            text-align: center;
            margin-bottom: 1.5em;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        
        .contact-links a {
            color: #FF4B4B;
            text-decoration: none;
            font-weight: bold;
            font-size: 1em;
            white-space: nowrap;
        }
        
        @media (max-width: 768px) {
            .contact-links {
                gap: 8px;
            }
            .contact-links a {
                font-size: 0.9em;
            }
        }
        
        @media (max-width: 480px) {
            .contact-links {
                flex-direction: column;
                gap: 5px;
                margin-bottom: 1em;
            }
            .contact-links a {
                font-size: 0.85em;
                display: block;
            }
        }
        
        .contact-links a:hover {
            text-decoration: underline;
        }
        
        .profile-photo {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            border: 4px solid #FF4B4B;
            object-fit: cover;
            margin: 2rem auto 1em;
            display: block;
        }
        
        @media (max-width: 768px) {
            .profile-photo {
                width: 120px;
                height: 120px;
                border: 3px solid #FF4B4B;
            }
        }
        
        @media (max-width: 480px) {
            .profile-photo {
                width: 100px;
                height: 100px;
                border: 2px solid #FF4B4B;
                margin-bottom: 0.8em;
            }
        }
        
        .footer-contact {
            text-align: center;
            color: #FFFFFF;
            margin-top: 2em;
            font-size: 0.95em;
        }
        
        @media (max-width: 768px) {
            .footer-contact {
                margin-top: 1.5em;
                font-size: 0.9em;
            }
        }
        
        @media (max-width: 480px) {
            .footer-contact {
                margin-top: 1em;
                font-size: 0.8em;
            }
        }
        
        .footer-contact a {
            color: #FF4B4B;
            text-decoration: none;
            margin: 0 10px;
            white-space: nowrap;
        }
        
        @media (max-width: 480px) {
            .footer-contact a {
                display: block;
                margin: 5px 0;
            }
        }
        
        .footer-contact a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# SIDEBAR PADRONIZADA - Ícone Home + Menu Expansível
# ============================================================================
with st.sidebar:
    # Ícone de casa como "Home" no topo
    st.markdown('<div class="home-title">🏠</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align: center; font-size: 0.9em; color: #FAFAFA; margin-top: -10px;">GoodLuke AI Hub</p>',
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Menu expansível com todas as aplicações
    with st.expander("📱 **Aplicações**", expanded=False):
        for app in APPS_DO_HUB:
            label = f"{app['icon']} {app['num']}. {app['nome']}"
            if st.button(label, key=f"sidebar_app_{app['num']}", use_container_width=True):
                st.switch_page(app['page'])
    
    st.markdown("---")
    
    # Info de contato na sidebar
    st.markdown(
        """
        <div style="text-align: center; font-size: 0.85em; color: #A3A8B4; margin-top: 1em;">
            <div style="color: #FF4B4B; font-weight: bold; margin-bottom: 0.5em;">Lenon de Paula</div>
            <div>📧 lenondpaula@gmail.com</div>
            <div style="margin-top: 0.5em;">
                <a href="https://wa.me/5555981359099" style="color: #FF4B4B; text-decoration: none;">💬 WhatsApp</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# CONTEÚDO PRINCIPAL
# ============================================================================

# Header de Impacto com Foto e Contato
st.markdown("""
    <img src="https://github.com/lenondpaula.png" alt="Lenon de Paula" class="profile-photo">
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-title">Lenon de Paula</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-subtitle">Engenharia de Dados · Machine Learning · IA Generativa</div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="contact-links">
        <a href="mailto:lenondpaula@gmail.com">📧 lenondpaula@gmail.com</a>
        <a href="https://wa.me/5555981359099">💬 +55 (55) 98135-9099</a>
        <a href="https://t.me/+5555981359099">✈️ Telegram</a>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
Bem-vindo ao meu laboratório de inovação. Aqui, a **Engenharia de Dados** encontra a **IA Generativa** para criar soluções que não apenas processam informação, mas geram valor de negócio real. 
Focado na pirâmide da sabedoria: do dado à estratégia.
""")

st.divider()

# Definição dos Projetos (1 a 9)
projetos = [
    {"id": 1, "nome": "Manutenção Preditiva", "tag": "Indústria 4.0", "desc": "Previsão de falhas em máquinas térmicas para redução de downtime."},
    {"id": 2, "nome": "Análise de Sentimentos", "tag": "NLP", "desc": "Monitorização de marca e feedback de clientes em tempo real."},
    {"id": 3, "nome": "Vendedor Automático", "tag": "E-commerce", "desc": "Motor de recomendação focado na cauda longa e aumento de ticket médio."},
    {"id": 4, "nome": "Oráculo de Vendas", "tag": "BI Preditivo", "desc": "Previsão de séries temporais para planeamento financeiro robusto."},
    {"id": 5, "nome": "Assistente Corporativo", "tag": "RAG / LLM", "desc": "Chatbot especializado em documentos internos (PDFs) sem alucinações."},
    {"id": 6, "nome": "GIG-Master AI", "tag": "Show Business", "desc": "Otimização logística de tours e plano de marketing automatizado."},
    {"id": 7, "nome": "Burger-Flow Intel", "tag": "Franquias", "desc": "Engenharia de menu e previsão de stock para redução de desperdício."},
    {"id": 8, "nome": "PoA-Insight Explorer", "tag": "Smart Cities", "desc": "Guia turístico contextual que reage ao clima e horário de Porto Alegre."},
    {"id": 9, "nome": "Visual-On-Demand", "tag": "Gig Economy", "desc": "Marketplace de fotógrafos com match baseado em estilo visual (IA)."}
]

# Grid de Projetos (3 colunas)
cols = st.columns(3)

for i, p in enumerate(projetos):
    with cols[i % 3]:
        st.markdown(f"""
            <div class="project-card">
                <span class="project-tag">{p['tag']}</span>
                <div class="project-title">{p['nome']}</div>
                <p class="project-desc">{p['desc']}</p>
            </div>
        """, unsafe_allow_html=True)
        # O botão de abrir a aplicação
        if st.button(f"Abrir Aplicação {p['id']}", key=f"btn_{p['id']}"):
            st.info(f"A carregar o módulo: {p['nome']}...")

st.divider()

# Rodapé com Contatos Destacados
st.markdown("""
<div class="footer-contact">
    <div style="font-weight: bold; color: #FF4B4B; font-size: 1.15em; margin-bottom: 0.5em;">
        © 2026 Lenon de Paula
    </div>
    <div style="margin-bottom: 0.8em;">
        <a href="mailto:lenondpaula@gmail.com">📧 lenondpaula@gmail.com</a>
    </div>
    <div style="margin-bottom: 0.3em;">
        📱 <strong>+55 (55) 98135-9099</strong>
    </div>
    <div>
        <a href="https://wa.me/5555981359099">💬 WhatsApp</a> |
        <a href="https://t.me/+5555981359099">✈️ Telegram</a>
    </div>
    <hr style="opacity: 0.3; margin-top: 1em;">
    <small>Desenvolvido com <b>IA-Augmented Engineering</b>. Foco em arquitetura, curadoria e resultados rápidos.</small>
</div>
""", unsafe_allow_html=True)
