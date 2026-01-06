"""
Jornal-Agent - Página de Logs.

Visualiza logs de execução do agente.
"""

import streamlit as st
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Logs | Jornal-Agent",
    page_icon="📝",
    layout="wide",
)

# CSS
st.markdown("""
<style>
    :root {
        --primary: #1a1a2e;
        --secondary: #16213e;
        --bg-card: #1e1e2d;
        --border: #2d2d3d;
        --text: #eaeaea;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    h1, h2, h3 {
        color: var(--text) !important;
    }
    
    .log-viewer {
        background: #0d1117;
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 0.85rem;
        line-height: 1.6;
        overflow-x: auto;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .log-line {
        margin: 0;
        padding: 2px 0;
    }
    
    .log-info { color: #58a6ff; }
    .log-warning { color: #d29922; }
    .log-error { color: #f85149; }
    .log-success { color: #3fb950; }
    .log-debug { color: #8b949e; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_FILE = OUTPUT_DIR / "jornal-agent.log"

st.title("📝 Logs de Execução")

if not LOG_FILE.exists():
    st.info("Nenhum log disponível. Execute o agente para gerar logs.")
    st.stop()

# Filtros
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    search = st.text_input("🔍 Buscar", placeholder="Filtrar logs...")

with col2:
    level_filter = st.multiselect(
        "Nível",
        ["INFO", "WARNING", "ERROR", "SUCCESS", "DEBUG"],
        default=["INFO", "WARNING", "ERROR", "SUCCESS"],
    )

with col3:
    lines_limit = st.selectbox("Linhas", [100, 250, 500, 1000], index=1)

# Carrega e filtra logs
try:
    content = LOG_FILE.read_text(encoding="utf-8", errors="ignore")
    lines = content.strip().split("\n")
    
    # Filtra últimas N linhas
    lines = lines[-lines_limit:]
    
    # Aplica filtros
    filtered_lines = []
    for line in lines:
        # Filtro de busca
        if search and search.lower() not in line.lower():
            continue
        
        # Filtro de nível
        line_upper = line.upper()
        if not any(level in line_upper for level in level_filter):
            continue
        
        filtered_lines.append(line)
    
    # Estatísticas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de linhas", len(lines))
    
    with col2:
        st.metric("Filtradas", len(filtered_lines))
    
    with col3:
        errors = sum(1 for l in lines if "ERROR" in l.upper())
        st.metric("Erros", errors)
    
    with col4:
        mtime = datetime.fromtimestamp(LOG_FILE.stat().st_mtime)
        st.metric("Atualizado", mtime.strftime("%H:%M:%S"))
    
    st.divider()
    
    # Exibe logs com cores
    if filtered_lines:
        log_html = []
        for line in filtered_lines:
            # Determina classe de cor
            line_upper = line.upper()
            if "ERROR" in line_upper:
                css_class = "log-error"
            elif "WARNING" in line_upper:
                css_class = "log-warning"
            elif "SUCCESS" in line_upper:
                css_class = "log-success"
            elif "DEBUG" in line_upper:
                css_class = "log-debug"
            else:
                css_class = "log-info"
            
            # Escapa HTML
            safe_line = line.replace("<", "&lt;").replace(">", "&gt;")
            log_html.append(f'<p class="log-line {css_class}">{safe_line}</p>')
        
        st.markdown(
            f'<div class="log-viewer">{"".join(log_html)}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.warning("Nenhum log corresponde aos filtros.")
    
    # Download
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            "📥 Download Log Completo",
            content,
            file_name="jornal-agent.log",
            mime="text/plain",
        )
    
    with col2:
        if st.button("🗑️ Limpar Logs"):
            LOG_FILE.write_text("")
            st.rerun()

except Exception as e:
    st.error(f"Erro ao carregar logs: {e}")
