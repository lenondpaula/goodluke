"""
Hub de Criação - Lenon de Paula
Arquivo de entrada principal para Streamlit Cloud
"""

import streamlit as st
import sys
from pathlib import Path

# Adiciona o diretório src ao path para imports
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista
# ────────────────────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
:root {
    --primary: #0f172a;
    --secondary: #334155;
    --accent: #3b82f6;
    --bg: #f8fafc;
}
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.block-container {
    padding-top: 2rem;
    max-width: 900px;
}
h1 {
    color: var(--primary);
    font-weight: 700;
    letter-spacing: -0.5px;
}
.profile-card {
    text-align: center;
    padding: 2rem;
    margin-bottom: 2rem;
}
.profile-photo {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #e2e8f0;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.profile-name {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 0.5rem;
}
.profile-title {
    font-size: 1.1rem;
    color: var(--secondary);
    margin-bottom: 1rem;
}
.profile-contact {
    font-size: 0.95rem;
    color: var(--accent);
}
.profile-contact a {
    color: var(--accent);
    text-decoration: none;
}
.app-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: box-shadow 0.2s;
}
.app-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}
.app-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 0.5rem;
}
.app-desc {
    font-size: 0.9rem;
    color: var(--secondary);
    margin-bottom: 0.75rem;
}
.badge-active {
    background: #dcfce7;
    color: #166534;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
.badge-dev {
    background: #fef3c7;
    color: #92400e;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}
</style>
"""

APPS = [
    {
        "title": "🔧 App 1 — Sistema de Precaução Mecânica",
        "desc": "Modelo de Machine Learning para manutenção preditiva de equipamentos industriais.",
        "status": "active",
        "page": "pages/1_Sistema_de_Precaucao_Mecanica",
    },
    {
        "title": "📊 App 2 — Gestor de Reputação de Marca",
        "desc": "Monitor de reputação de marca com NLP para análise de menções em redes sociais.",
        "status": "active",
        "page": "pages/2_Gestor_de_Reputacao_de_Marca",
    },
    {
        "title": "🛒 App 3 — Que tal esse?",
        "desc": "Recomenda itens de nicho com filtragem colaborativa (SVD) para elevar ticket médio.",
        "status": "active",
        "page": "pages/3_Que_tal_esse",
    },
    {
        "title": "🔮 App 4 — O Oráculo de Vendas (BI Preditivo)",
        "desc": "Dashboard que projeta vendas do próximo mês com modelos de séries temporais (Prophet).",
        "status": "active",
        "page": "pages/4_O_Oraculo_de_Vendas",
    },
    {
        "title": "🤖 App 5 — O Assistente Corporativo",
        "desc": "Chatbot que lê PDFs e responde perguntas usando RAG (LangChain + ChromaDB).",
        "status": "active",
        "page": "pages/5_O_Assistente_Corporativo",
    },
]


def main():
    st.set_page_config(
        page_title="Lenon de Paula | Portfolio",
        page_icon="🚀",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Perfil ──────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="profile-card">
            <img src="https://github.com/lenondpaula.png" alt="Lenon de Paula" class="profile-photo">
            <div class="profile-name">Lenon de Paula</div>
            <div class="profile-title">Engenharia de Dados · Machine Learning · Automação</div>
            <div class="profile-contact">
                <a href="mailto:lenondpaula@gmail.com">lenondpaula@gmail.com</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("🚀 Aplicações")

    # ── Lista de Apps ───────────────────────────────────────────────────────────
    for app in APPS:
        badge = (
            '<span class="badge-active">✓ Disponível</span>'
            if app["status"] == "active"
            else '<span class="badge-dev">🔨 Em desenvolvimento</span>'
        )
        st.markdown(
            f"""
            <div class="app-card">
                <div class="app-title">{app["title"]}</div>
                <div class="app-desc">{app["desc"]}</div>
                {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if app["status"] == "active" and app["page"]:
            st.page_link(f"{app['page']}.py", label="Abrir aplicação →", icon="▶️")

    # ── Rodapé ──────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#64748b; font-size:0.85rem;">
            © 2026 Lenon de Paula · 
            <a href="mailto:lenondpaula@gmail.com" style="color:#3b82f6;">lenondpaula@gmail.com</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()

