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
    </style>
""", unsafe_allow_html=True)

# Header de Impacto
st.title("🚀 GoodLuke AI & Data Hub")
st.subheader("Transformando dados brutos em decisões estratégicas através de IA Avançada.")

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

# Rodapé Ético e Profissional
st.markdown("""
<div style="text-align: center; color: #555;">
    <small>Desenvolvido com <b>IA-Augmented Engineering</b>. Foco em arquitetura, curadoria e resultados rápidos.</small>
</div>
""", unsafe_allow_html=True)
