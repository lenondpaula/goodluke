"""
Jornal-Agent - Página de Visualização de Clipagens.

Exibe as clipagens geradas com formatação visual.
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Clipagens | Jornal-Agent",
    page_icon="📋",
    layout="wide",
)

# CSS Corporativo
st.markdown("""
<style>
    :root {
        --primary: #1a1a2e;
        --secondary: #16213e;
        --accent: #0f3460;
        --highlight: #e94560;
        --success: #00d26a;
        --text: #eaeaea;
        --text-muted: #8b8b8b;
        --bg-card: #1e1e2d;
        --border: #2d2d3d;
    }
    
    .stApp {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    h1, h2, h3 {
        color: var(--text) !important;
    }
    
    .clipagem-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .clipagem-item:hover {
        border-color: var(--highlight);
        transform: translateX(4px);
    }
    
    .clipagem-page {
        display: inline-block;
        background: var(--accent);
        color: var(--text);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 10px;
    }
    
    .clipagem-subject {
        color: var(--highlight);
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .clipagem-summary {
        color: var(--text);
        margin-top: 0.5rem;
        line-height: 1.5;
    }
    
    .date-selector {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 2rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Paths
BASE_DIR = Path(__file__).parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"

st.title("📋 Clipagens Geradas")

# Lista arquivos de clipagem
clipagem_files = sorted(OUTPUT_DIR.glob("clipagem-*.json"), reverse=True)

if not clipagem_files:
    st.info("Nenhuma clipagem gerada ainda. Execute o agente para gerar clipagens.")
    st.stop()

# Seletor de data
file_options = {f.stem.replace("clipagem-", ""): f for f in clipagem_files}
selected_date = st.selectbox(
    "Selecione a data",
    options=list(file_options.keys()),
    format_func=lambda x: datetime.strptime(x, "%Y%m%d").strftime("%d/%m/%Y"),
)

selected_file = file_options[selected_date]

# Carrega e exibe clipagem
try:
    data = json.loads(selected_file.read_text())
    
    # Métricas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Itens", len(data.get("items", [])))
    
    with col2:
        pages_info = data.get("pages", [])
        total_pages = len(pages_info)
        ocr_pages = sum(1 for p in pages_info if p.get("ocr_used"))
        st.metric("Páginas", f"{total_pages} ({ocr_pages} OCR)")
    
    with col3:
        avg_conf = sum(p.get("confidence", 0) for p in pages_info) / len(pages_info) if pages_info else 0
        st.metric("Confiança", f"{avg_conf:.0%}")
    
    st.divider()
    
    # Itens da clipagem
    items = data.get("items", [])
    
    if items:
        for item in items:
            st.markdown(f"""
            <div class="clipagem-item">
                <span class="clipagem-page">Página {item.get('page', '?')}</span>
                <span class="clipagem-subject">{item.get('subject', '').replace('**', '')}</span>
                <div class="clipagem-summary">{item.get('summary', '')}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Nenhum item na clipagem.")
    
    # Download
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        txt_file = OUTPUT_DIR / f"clipagem-{selected_date}.txt"
        if txt_file.exists():
            st.download_button(
                "📄 Download TXT",
                txt_file.read_text(),
                file_name=txt_file.name,
                mime="text/plain",
            )
    
    with col2:
        st.download_button(
            "📊 Download JSON",
            json.dumps(data, indent=2, ensure_ascii=False),
            file_name=selected_file.name,
            mime="application/json",
        )

except Exception as e:
    st.error(f"Erro ao carregar clipagem: {e}")
