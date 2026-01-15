# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Chatbot RAG - Assistente Corporativo
Interface Streamlit para perguntas sobre documentos PDF
Usa busca semântica (ChromaDB) + geração de respostas com Gemini API
"""

from pathlib import Path
import sys
import shutil

import streamlit as st

# Adiciona src ao path para imports
BASE_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE_DIR.parent
SRC_DIR = BASE_DIR / "src"
DB_DIR = BASE_DIR / "db_store"
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

from processador_pdf import processar_pdf_upload
from indexador import (
    criar_ou_carregar_vectorstore,
    indexar_documentos,
    buscar_com_scores,
    contar_documentos,
)
from shared.components import (  # noqa: E402
    SHARED_SIDEBAR_CSS,
    render_sidebar_header,
    render_sidebar_footer,
    render_rodape,
    render_instrucoes_uso,
)

# ────────────────────────────────────────────────────────────────────────────────
# CONFIGURAÇÕES
# ────────────────────────────────────────────────────────────────────────────────
MAX_FILE_SIZE_MB = 100  # Limite de 100MB por arquivo
GEMINI_MODEL_DEFAULT = "gemini-1.5-flash"  # Modelo rápido e eficiente do Google
GEMINI_API_KEY = "AIzaSyC6pihdReWGrWDB19LHqQSc-cHGtm9a0X8"  # API Key do Gemini


# ────────────────────────────────────────────────────────────────────────────────
# CSS corporativo minimalista (padrão do Hub)
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
    max-width: 1000px;
}
h1 {
    color: var(--primary);
    font-weight: 700;
    letter-spacing: -0.5px;
}
section[data-testid="stSidebar"] {
    background: var(--primary);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
    font-weight: 500;
}
/* File uploader - fundo escuro com texto claro */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #1e293b;
    border: 2px dashed #475569;
    border-radius: 8px;
    padding: 1rem;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] * {
    color: #e2e8f0 !important;
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
.chat-message {
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
}
.chat-user {
    background: #dbeafe;
    border: 1px solid #93c5fd;
}
.chat-assistant {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
}
.fonte-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}
.fonte-header {
    font-weight: 600;
    color: var(--primary);
    margin-bottom: 0.25rem;
}
.fonte-trecho {
    color: var(--secondary);
    font-size: 0.8rem;
}
.status-card {
    border-radius: 12px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: 1rem;
    font-weight: 700;
    margin: 0.5rem 0;
}
.status-ok {
    background: #065f46 !important;
    color: #ffffff !important;
    border: 1px solid #34d399;
}
.status-warning {
    background: #92400e !important;
    color: #ffffff !important;
    border: 1px solid #fbbf24;
}
.status-danger {
    background: #991b1b !important;
    color: #ffffff !important;
    border: 1px solid #f87171;
}
.groq-status {
    padding: 0.5rem;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    text-align: center;
    margin: 0.5rem 0;
}
.groq-online {
    background: #166534 !important;
    color: #ffffff !important;
}
.groq-offline {
    background: #991b1b !important;
    color: #ffffff !important;
}
/* Botão de limpeza (vermelho) */
.btn-danger {
    background: #dc2626 !important;
    border: 1px solid #b91c1c !important;
}
.btn-danger:hover {
    background: #b91c1c !important;
}
</style>
"""


# ────────────────────────────────────────────────────────────────────────────────
# FUNÇÕES GEMINI API
# ────────────────────────────────────────────────────────────────────────────────
def obter_gemini_api_key() -> str:
    """Obtém API key do Gemini de constante, secrets ou variável de ambiente."""
    import os
    
    # Primeiro tenta usar a constante definida
    if GEMINI_API_KEY and GEMINI_API_KEY.strip():
        return GEMINI_API_KEY
    
    # Tenta obter de secrets do Streamlit
    try:
        if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
            return st.secrets['GEMINI_API_KEY']
    except Exception:
        pass
    
    # Fallback para variável de ambiente
    return os.getenv('GEMINI_API_KEY', '')


def verificar_gemini() -> bool:
    """Verifica se a API do Gemini está configurada."""
    api_key = obter_gemini_api_key()
    return bool(api_key and api_key.strip())


def gerar_resposta_gemini(pergunta: str, contextos: list, modelo: str = GEMINI_MODEL_DEFAULT) -> str:
    """Gera resposta usando Gemini API."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = obter_gemini_api_key()
        if not api_key:
            return "❌ Chave API do Gemini não configurada."
        
        # Monta o contexto
        contexto_texto = "\n\n".join([
            f"Trecho {i+1} (de {doc.metadata.get('fonte', 'documento')}):\n{doc.page_content}"
            for i, (doc, score) in enumerate(contextos)
        ])
        
        # Prompt otimizado para RAG
        prompt = f"""Você é um assistente corporativo inteligente. Use APENAS as informações do contexto abaixo para responder à pergunta. Se a informação não estiver no contexto, diga que não encontrou a informação nos documentos.

CONTEXTO:
{contexto_texto}

PERGUNTA: {pergunta}

RESPOSTA (seja conciso e objetivo):"""

        llm = ChatGoogleGenerativeAI(
            model=modelo,
            google_api_key=api_key,
            temperature=0.3,
            max_output_tokens=1024,
        )
        
        resposta = llm.invoke(prompt)
        return resposta.content.strip()
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta: {str(e)}"


def gerar_resposta_sem_llm(pergunta: str, contextos: list) -> str:
    """Fallback quando Gemini não está disponível."""
    if not contextos:
        return "Não encontrei informações relevantes nos documentos para responder sua pergunta."
    
    resposta = "📚 **Trechos relevantes encontrados:**\n\n"
    
    for i, (doc, score) in enumerate(contextos, 1):
        trecho = doc.page_content.strip()
        fonte = doc.metadata.get("fonte", "Documento")
        resposta += f"**Trecho {i}** (de *{fonte}*):\n"
        resposta += f"> {trecho}\n\n"
    
    resposta += "---\n"
    resposta += "*ℹ️ Configure a API do Gemini para respostas elaboradas por IA.*"
    
    return resposta


# ────────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DE GERENCIAMENTO
# ────────────────────────────────────────────────────────────────────────────────
def limpar_base_documentos():
    """Remove todos os documentos indexados."""
    try:
        if DB_DIR.exists():
            shutil.rmtree(DB_DIR)
            st.session_state.vectorstore = None
            return True
    except Exception as e:
        st.error(f"Erro ao limpar base: {str(e)}")
    return False


def inicializar_sessao():
    """Inicializa variáveis de sessão do Streamlit."""
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "fontes_ultima_resposta" not in st.session_state:
        st.session_state.fontes_ultima_resposta = []


def carregar_vectorstore():
    """Carrega ou cria a base vetorial."""
    if st.session_state.vectorstore is None:
        with st.spinner("🔮 Carregando base de conhecimento..."):
            st.session_state.vectorstore = criar_ou_carregar_vectorstore()
    return st.session_state.vectorstore


def processar_upload(arquivo_pdf):
    """Processa PDF enviado pelo usuário."""
    if arquivo_pdf is None:
        return
    
    # Verifica tamanho do arquivo
    file_size_mb = len(arquivo_pdf.getvalue()) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"❌ Arquivo muito grande ({file_size_mb:.1f}MB). Máximo: {MAX_FILE_SIZE_MB}MB")
        return
    
    with st.spinner(f"📄 Processando {arquivo_pdf.name}..."):
        chunks = processar_pdf_upload(arquivo_pdf.getvalue(), arquivo_pdf.name)
        
        if not chunks:
            st.error("❌ Não foi possível extrair texto do PDF.")
            return
        
        st.session_state.vectorstore = indexar_documentos(chunks, limpar_base=False)
        st.success(f"✅ {len(chunks)} trechos indexados de '{arquivo_pdf.name}'!")


def processar_pergunta(pergunta: str):
    """Processa pergunta do usuário e gera resposta."""
    vectorstore = carregar_vectorstore()
    
    num_docs = contar_documentos(vectorstore)
    if num_docs == 0:
        return "⚠️ Nenhum documento indexado. Faça upload de um PDF primeiro!", []
    
    with st.spinner("🔍 Buscando informações relevantes..."):
        resultados = buscar_com_scores(pergunta, k=3, vectorstore=vectorstore)
    
    if not resultados:
        return "Não encontrei informações relevantes para sua pergunta.", []
    
    # Usa Gemini se disponível, senão mostra chunks
    if verificar_gemini():
        with st.spinner(f"⚡ Gerando resposta com Gemini..."):
            resposta = gerar_resposta_gemini(pergunta, resultados, GEMINI_MODEL_DEFAULT)
    else:
        resposta = gerar_resposta_sem_llm(pergunta, resultados)
    
    return resposta, resultados


# ────────────────────────────────────────────────────────────────────────────────
# RENDERIZAÇÃO
# ────────────────────────────────────────────────────────────────────────────────
def render_chat():
    """Renderiza histórico de chat."""
    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-message chat-user">👤 <strong>Você:</strong> {msg["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-message chat-assistant">🤖 <strong>Assistente:</strong><br>{msg["content"]}</div>',
                unsafe_allow_html=True
            )


def render_fontes(fontes: list):
    """Renderiza as fontes usadas na última resposta."""
    if not fontes:
        st.caption("Nenhuma fonte disponível")
        return
    
    for i, (doc, score) in enumerate(fontes, 1):
        fonte = doc.metadata.get("fonte", "N/A")
        pagina = doc.metadata.get("page", "N/A")
        trecho = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
        similaridade = max(0, min(100, int((1 - score) * 100)))
        
        st.markdown(
            f"""
            <div class="fonte-card">
                <div class="fonte-header">📄 {fonte} (pág. {pagina})</div>
                <div class="fonte-trecho">{trecho}</div>
                <div style="margin-top:0.5rem;">
                    <span style="background:#dbeafe; color:#1e40af; padding:0.15rem 0.5rem; border-radius:8px; font-size:0.7rem;">
                        Relevância: {similaridade}%
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ────────────────────────────────────────────────────────────────────────────────
# APP PRINCIPAL
# ────────────────────────────────────────────────────────────────────────────────
def render_app():
    """Função principal do chatbot."""
    
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(SHARED_SIDEBAR_CSS, unsafe_allow_html=True)
    inicializar_sessao()
    
    st.title("🤖 Assistente Corporativo")
    st.markdown("Faça perguntas sobre seus documentos PDF usando **RAG** (Retrieval-Augmented Generation)")
    
    # Instruções de uso
    render_instrucoes_uso(
        instrucoes=[
            "Faça upload de PDFs na sidebar (máx. 100MB)",
            "Aguarde a indexação dos documentos",
            "Digite sua pergunta no chat",
        ],
        ferramentas_sidebar=[
            "**📤 Upload PDF** – Envie documentos para indexar",
            "**📊 Status** – Quantidade de docs indexados",
            "**⚡ Modelo** – Gemini API (gemini-1.5-flash)",
            "**🗑️ Limpar** – Remove documentos ou conversa",
        ]
    )
    
    with st.container():
        st.markdown(
            """
            <div style="background:#f1f5f9; border-left:4px solid #8b5cf6; padding:1rem 1.25rem; border-radius:6px; margin-bottom:1.5rem;">
                <strong>O que é RAG?</strong><br>
                <em>Retrieval-Augmented Generation</em> combina busca semântica com IA generativa.
                O sistema encontra trechos relevantes nos seus documentos e usa como contexto para responder.<br><br>
                <strong>Como usar</strong><br>
                1. Faça upload de um PDF na barra lateral<br>
                2. Aguarde a indexação<br>
                3. Faça perguntas sobre o conteúdo!
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # ── Sidebar Header (Home + Menu Aplicações) ─────────────────────────────────
    render_sidebar_header()

    # ── Conteúdo específico do app na sidebar ───────────────────────────────────
    with st.sidebar:
        st.markdown("### 📁 Documentos")
        
        arquivo_pdf = st.file_uploader(
            "Upload PDF (máx. 100MB)",
            type=["pdf"],
            help=f"Tamanho máximo: {MAX_FILE_SIZE_MB}MB"
        )
        
        if arquivo_pdf:
            file_size_mb = len(arquivo_pdf.getvalue()) / (1024 * 1024)
            st.caption(f"📄 {arquivo_pdf.name} ({file_size_mb:.1f}MB)")
            
            if st.button("📤 Indexar documento", use_container_width=True):
                processar_upload(arquivo_pdf)
        
        st.markdown("---")
        
        # Status da base
        st.markdown("### 📊 Status da Base")
        vectorstore = carregar_vectorstore()
        num_docs = contar_documentos(vectorstore)
        
        st.metric("Documentos indexados", num_docs)
        
        if num_docs > 0:
            st.markdown('<div class="status-card status-ok">✅ Pronto para perguntas</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card status-warning">⚠️ Base vazia</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Status do Gemini
        st.markdown("### ⚡ Modelo de IA")
        gemini_disponivel = verificar_gemini()
        
        if gemini_disponivel:
            st.markdown('<div class="gemini-status gemini-online">✅ Gemini API Conectada</div>', unsafe_allow_html=True)
            st.caption(f"Modelo: `{GEMINI_MODEL_DEFAULT}`")
        else:
            st.markdown('<div class="gemini-status gemini-offline">❌ Gemini não configurado</div>', unsafe_allow_html=True)
            st.info(
                """
                Para respostas por IA:
                1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
                2. Gere uma API key
                3. Adicione ao `.streamlit/secrets.toml`:
                ```toml
                GEMINI_API_KEY = "sua_chave"
                ```
                """
            )
        
        st.markdown("---")
        
        # Fontes da última resposta
        st.markdown("### 📚 Fontes Utilizadas")
        render_fontes(st.session_state.fontes_ultima_resposta)
        
        st.markdown("---")
        
        # Ações de limpeza
        st.markdown("### 🗑️ Gerenciamento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💬 Limpar Chat", use_container_width=True, help="Limpa histórico de conversa"):
                st.session_state.mensagens = []
                st.session_state.fontes_ultima_resposta = []
                st.rerun()
        
        with col2:
            if num_docs > 0:
                if st.button("📁 Limpar Base", use_container_width=True, help="Remove todos os documentos indexados"):
                    if limpar_base_documentos():
                        st.success("✅ Base limpa!")
                        st.rerun()

    # ── Sidebar Footer (Contato + Copyright) ────────────────────────────────────
    render_sidebar_footer()
    
    # ── Chat ────────────────────────────────────────────────────────────────────
    st.markdown("---")
    render_chat()
    
    pergunta = st.chat_input("Digite sua pergunta sobre os documentos...")
    
    if pergunta:
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        
        resposta, fontes = processar_pergunta(pergunta)
        
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        st.session_state.fontes_ultima_resposta = fontes
        st.rerun()

    # Footer
    render_rodape(
        titulo_app="🤖 Assistente Corporativo RAG",
        subtitulo="Perguntas e respostas sobre documentos com busca semântica",
        tecnologias="LangChain + ChromaDB + HuggingFace + Gemini"
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Assistente Corporativo RAG",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_app()
