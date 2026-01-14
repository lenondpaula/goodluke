import streamlit as st

# Configuração da página
st.set_page_config(page_title="GoodLuke AI Hub", layout="wide", page_icon="🚀")

# CSS para tornar o portfólio "Arrojado"
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
        }
        .stButton>button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #FF4B4B;
            color: white;
        }
        .project-card {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF4B4B;
            margin-bottom: 20px;
            height: 300px;
        }
        .project-title {
            color: #FF4B4B;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .project-tag {
            font-size: 12px;
            background-color: #31333F;
            padding: 4px 8px;
            border-radius: 15px;
            color: #A3A8B4;
        }
        .header-title {
            color: #FF4B4B;
            font-size: 3em;
            font-weight: bold;
            text-align: center;
            margin-bottom: 0.2em;
        }
        .header-subtitle {
            color: #FFFFFF;
            font-size: 1.2em;
            text-align: center;
            margin-bottom: 0.3em;
        }
        .contact-links {
            text-align: center;
            margin-bottom: 1.5em;
        }
        .contact-links a {
            color: #FF4B4B;
            text-decoration: none;
            margin: 0 15px;
            font-weight: bold;
            font-size: 1.1em;
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
            margin: 0 auto 1em;
            display: block;
        }
        .footer-contact {
            text-align: center;
            color: #FFFFFF;
            margin-top: 2em;
            font-size: 0.95em;
        }
        .footer-contact a {
            color: #FF4B4B;
            text-decoration: none;
            margin: 0 10px;
        }
        .footer-contact a:hover {
            text-decoration: underline;
        }
    </style>
""", unsafe_allow_html=True)

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
        <a href="mailto:lenondpaula@gmail.com">📧 lenondpaula@gmail.com</a><br>
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
                <p style="color: #FAFAFA; font-size: 14px;">{p['desc']}</p>
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
