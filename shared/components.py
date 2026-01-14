# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Componentes compartilhados para todas as aplicações do Hub
Inclui sidebar padronizada, rodapé e estilos CSS comuns
"""

import streamlit as st

# ============================================================================
# CSS COMPARTILHADO - Sidebar uniforme para todos os apps
# ============================================================================

SHARED_SIDEBAR_CSS = """
<style>
/* Sidebar uniforme - Tema escuro corporativo */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-weight: 600;
}

section[data-testid="stSidebar"] label {
    font-weight: 500;
    color: #cbd5e1 !important;
}

section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #334155;
    border: 1px solid #475569;
}

section[data-testid="stSidebar"] .stSlider > div > div {
    background: #334155;
}

section[data-testid="stSidebar"] hr {
    border-color: #334155;
}

/* Botões na sidebar */
section[data-testid="stSidebar"] button {
    background: #3b82f6 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] button:hover {
    background: #2563eb !important;
}

/* File uploader na sidebar */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #1e293b;
    border: 2px dashed #475569;
    border-radius: 8px;
    padding: 0.75rem;
}

/* Expander na sidebar */
section[data-testid="stSidebar"] .streamlit-expanderHeader {
    background: #1e293b;
    border-radius: 8px;
}
</style>
"""

# ============================================================================
# DEFINIÇÃO DOS APPS DO HUB
# ============================================================================

APPS_DO_HUB = [
    {"num": 1, "nome": "Precaução Mecânica", "icon": "🔧", "page": "pages/1_Sistema_de_Precaucao_Mecanica.py"},
    {"num": 2, "nome": "Reputação de Marca", "icon": "📊", "page": "pages/2_Gestor_de_Reputacao_de_Marca.py"},
    {"num": 3, "nome": "Sugestão de Compra", "icon": "🛒", "page": "pages/3_Sugestao_de_compra.py"},
    {"num": 4, "nome": "Oráculo de Vendas", "icon": "🔮", "page": "pages/4_O_Oraculo_de_Vendas.py"},
    {"num": 5, "nome": "Assistente Corporativo", "icon": "🤖", "page": "pages/5_O_Assistente_Corporativo.py"},
    {"num": 6, "nome": "GIG-Master AI", "icon": "🎸", "page": "pages/6_GIG_Master_AI.py"},
    {"num": 7, "nome": "Burger-Flow Intel", "icon": "🍔", "page": "pages/7_Burger_Flow_Intelligence.py"},
    {"num": 8, "nome": "PoA-Insight Explorer", "icon": "🗺️", "page": "pages/8_PoA_Insight_Explorer.py"},
    {"num": 9, "nome": "Visual-On-Demand", "icon": "📸", "page": "pages/9_Visual_On_Demand.py"},
]


def render_sidebar_navegacao(app_atual: int = None):
    """
    Renderiza o menu de navegação na sidebar.
    
    Args:
        app_atual: Número do app atual (1-9) para destacar no menu
    """
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        
        with st.expander("📱 **Aplicações**", expanded=False):
            # Link para Home
            if st.button("🏠 Home", key="nav_home", use_container_width=True):
                st.switch_page("streamlit_app.py")
            
            st.markdown("---")
            
            # Links para cada app
            for app in APPS_DO_HUB:
                label = f"{app['icon']} {app['num']}. {app['nome']}"
                disabled = (app['num'] == app_atual)
                
                if st.button(label, key=f"nav_app_{app['num']}", use_container_width=True, disabled=disabled):
                    st.switch_page(app['page'])


def render_rodape(
    titulo_app: str,
    subtitulo: str,
    tecnologias: str = "Streamlit + Python + Machine Learning"
):
    """
    Renderiza o rodapé padronizado para cada aplicação.
    
    Args:
        titulo_app: Nome curto do app (ex: "Visual-On-Demand")
        subtitulo: Descrição curta do propósito
        tecnologias: Stack tecnológico usado
    """
    st.markdown("---")
    st.markdown(
        f"""
        <div style="text-align: center; padding: 1.5rem 0; color: #64748b;">
            <div style="font-size: 1.1rem; font-weight: 600; color: #3b82f6; margin-bottom: 0.25rem;">
                {titulo_app}
            </div>
            <div style="font-size: 0.9rem; margin-bottom: 1rem; font-style: italic;">
                {subtitulo}
            </div>
            <div style="margin-bottom: 1rem;">
                Desenvolvido por <strong>Lenon de Paula</strong> · 
                <a href="mailto:lenondpaula@gmail.com" style="color: #3b82f6; text-decoration: none;">
                    lenondpaula@gmail.com
                </a>
            </div>
            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.75rem;">
                {tecnologias}
            </div>
            <div style="font-size: 0.85rem; color: #64748b;">
                © 2026 Lenon de Paula
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_instrucoes_uso(instrucoes: list[str], ferramentas_sidebar: list[str] = None):
    """
    Renderiza uma seção de instruções de uso.
    
    Args:
        instrucoes: Lista de passos para usar o app
        ferramentas_sidebar: Lista de ferramentas disponíveis na sidebar
    """
    with st.expander("📖 **Como usar esta aplicação**", expanded=False):
        st.markdown("**Passos:**")
        for i, instrucao in enumerate(instrucoes, 1):
            st.markdown(f"{i}. {instrucao}")
        
        if ferramentas_sidebar:
            st.markdown("")
            st.markdown("**🔧 Ferramentas na Sidebar:**")
            for ferramenta in ferramentas_sidebar:
                st.markdown(f"• {ferramenta}")
