"""
Jornal-Agent Dashboard - Página Principal.

Dashboard corporativa para gerenciamento do Jornal-Agent.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Jornal-Agent | Dashboard",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────────────────────
# CSS Corporativo Minimalista (Tema Escuro)
# ────────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --primary: #1a1a2e;
        --secondary: #16213e;
        --accent: #0f3460;
        --highlight: #e94560;
        --success: #00d26a;
        --warning: #ffc107;
        --text: #eaeaea;
        --text-muted: #8b8b8b;
        --bg-card: #1e1e2d;
        --border: #2d2d3d;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    [data-testid="stSidebar"] {
        background: var(--bg-card);
        border-right: 1px solid var(--border);
    }
    
    h1, h2, h3 {
        color: var(--text) !important;
        font-weight: 600 !important;
    }
    
    .hero-section {
        text-align: center;
        padding: 3rem 0;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-muted);
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .status-card:hover {
        border-color: var(--highlight);
        transform: translateY(-4px);
    }
    
    .status-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    .status-title {
        font-size: 1rem;
        color: var(--text-muted);
        margin-bottom: 0.5rem;
    }
    
    .status-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
    }
    
    .status-success { color: var(--success) !important; }
    .status-warning { color: var(--warning) !important; }
    .status-error { color: var(--highlight) !important; }
    
    .quick-action {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .quick-action:hover {
        background: var(--accent);
        border-color: var(--accent);
    }
    
    .quick-action-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .quick-action-title {
        color: var(--text);
        font-weight: 500;
    }
    
    .recent-activity {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
    }
    
    .activity-item {
        display: flex;
        align-items: center;
        padding: 0.75rem 0;
        border-bottom: 1px solid var(--border);
    }
    
    .activity-item:last-child {
        border-bottom: none;
    }
    
    .activity-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-size: 1.2rem;
    }
    
    .activity-success { background: rgba(0, 210, 106, 0.15); }
    .activity-error { background: rgba(233, 69, 96, 0.15); }
    
    .activity-text {
        flex: 1;
    }
    
    .activity-title {
        color: var(--text);
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    .activity-time {
        color: var(--text-muted);
        font-size: 0.8rem;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "config"


def get_status() -> dict:
    """Obtém status da última execução."""
    status_file = OUTPUT_DIR / "last-run-status.json"
    if status_file.exists():
        try:
            return json.loads(status_file.read_text())
        except:
            pass
    return {}


def count_clipagens() -> int:
    """Conta clipagens geradas."""
    if OUTPUT_DIR.exists():
        return len(list(OUTPUT_DIR.glob("clipagem-*.json")))
    return 0


def get_config_status() -> dict:
    """Verifica status das configurações."""
    config_file = CONFIG_DIR / "settings.json"
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
            return {
                "jornal": bool(config.get("jornal_user") and config.get("jornal_pass")),
                "llm": bool(config.get("llm_api_key")),
                "whatsapp": bool(config.get("whatsapp_token")),
            }
        except:
            pass
    return {"jornal": False, "llm": False, "whatsapp": False}


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <div style="font-size: 2.5rem;">📰</div>
        <h2 style="margin: 0.5rem 0 0 0; font-size: 1.3rem;">Jornal-Agent</h2>
        <p style="color: #8b8b8b; font-size: 0.85rem; margin: 0;">Dashboard</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Status rápido
    status = get_status()
    config_status = get_config_status()
    
    if status.get("success"):
        st.success("✓ Sistema operacional")
    elif status:
        st.error("✗ Última execução falhou")
    else:
        st.warning("○ Nenhuma execução")
    
    st.divider()
    
    # Links de navegação
    st.caption("MENU")
    st.page_link("app.py", label="🏠 Início", icon=None)
    st.page_link("pages/2_Clipagens.py", label="📋 Clipagens")
    st.page_link("pages/3_Logs.py", label="📝 Logs")
    st.page_link("jornal_agent.py", label="⚙️ Configurações")
    
    st.divider()
    
    st.caption("v1.0.0")


# ════════════════════════════════════════════════════════════════════════════════
# CONTEÚDO PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════════

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="hero-title">📰 Jornal-Agent</div>
    <div class="hero-subtitle">Automação inteligente de clipagem de jornal</div>
</div>
""", unsafe_allow_html=True)

# Status Cards
status = get_status()
config_status = get_config_status()

col1, col2, col3, col4 = st.columns(4)

with col1:
    if status.get("success"):
        icon = "✅"
        value = "OK"
        css_class = "status-success"
    elif status:
        icon = "❌"
        value = "Erro"
        css_class = "status-error"
    else:
        icon = "⏸️"
        value = "Aguardando"
        css_class = "status-warning"
    
    st.markdown(f"""
    <div class="status-card">
        <div class="status-icon">{icon}</div>
        <div class="status-title">STATUS</div>
        <div class="status-value {css_class}">{value}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_clipagens = count_clipagens()
    st.markdown(f"""
    <div class="status-card">
        <div class="status-icon">📋</div>
        <div class="status-title">CLIPAGENS</div>
        <div class="status-value">{total_clipagens}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    pages = status.get("phases", {}).get("processing", {}).get("total_pages", 0)
    st.markdown(f"""
    <div class="status-card">
        <div class="status-icon">📄</div>
        <div class="status-title">PÁGINAS</div>
        <div class="status-value">{pages}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    items = status.get("phases", {}).get("processing", {}).get("total_items", 0)
    st.markdown(f"""
    <div class="status-card">
        <div class="status-icon">📌</div>
        <div class="status-title">ITENS</div>
        <div class="status-value">{items}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Duas colunas: Ações rápidas e Atividade recente
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("### ⚡ Ações Rápidas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Executar (Teste)", use_container_width=True, type="primary"):
            st.switch_page("jornal_agent.py")
    
    with col2:
        if st.button("⚙️ Configurações", use_container_width=True):
            st.switch_page("jornal_agent.py")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Ver Clipagens", use_container_width=True):
            st.switch_page("pages/2_Clipagens.py")
    
    with col2:
        if st.button("📝 Ver Logs", use_container_width=True):
            st.switch_page("pages/3_Logs.py")
    
    # Status de configuração
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔧 Configurações")
    
    checks = [
        ("Credenciais do Jornal", config_status.get("jornal", False)),
        ("API Key do LLM", config_status.get("llm", False)),
        ("WhatsApp API", config_status.get("whatsapp", False)),
    ]
    
    for name, configured in checks:
        if configured:
            st.markdown(f"✅ {name}")
        else:
            st.markdown(f"⚠️ {name} - *Pendente*")

with col_right:
    st.markdown("### 📊 Última Execução")
    
    if status:
        # Timestamp
        if status.get("timestamp"):
            try:
                dt = datetime.fromisoformat(status["timestamp"])
                st.info(f"📅 {dt.strftime('%d/%m/%Y às %H:%M:%S')}")
            except:
                pass
        
        # Fases
        phases = status.get("phases", {})
        
        for phase_name, phase_data in phases.items():
            success = phase_data.get("success", False)
            icon = "✅" if success else "❌"
            
            with st.expander(f"{icon} {phase_name.title()}", expanded=not success):
                for key, value in phase_data.items():
                    if key != "success":
                        st.caption(f"**{key}:** {value}")
        
        # Erro
        if status.get("error"):
            st.error(f"**Erro:** {status['error']}")
    else:
        st.info("Nenhuma execução registrada. Execute o agente para ver os resultados.")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.caption("📰 Jornal-Agent | Automação de Clipagem | © 2026")
