# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Chatbot RAG - Assistente Corporativo
Interface Streamlit para perguntas sobre documentos PDF
Usa busca semântica (ChromaDB) + geração de respostas com Ollama
"""

from pathlib import Path
import sys

import streamlit as st

# Adiciona src ao path para imports
BASE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = BASE_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

from processador_pdf import processar_pdf_upload
from indexador import (
    criar_ou_carregar_vectorstore,
    indexar_documentos,
    buscar_com_scores,
    contar_documentos,
)


def eh_streamlit_cloud() -> bool:
    """Detecta se está executando no Streamlit Cloud."""
    import os
    return (
        "STREAMLIT_RUNTIME_ENV" in os.environ 
        or "STREAMLIT_SERVER_HEADLESS" in os.environ
        or os.path.exists("/.dockerenv")
    )


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
/* Botões na sidebar - estilo escuro */
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
    margin: 1rem 0;
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
.ollama-status {
    padding: 0.75rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 700;
    text-align: center;
    margin: 0.5rem 0;
}
.ollama-online {
    background: #166534 !important;
    color: #ffffff !important;
}
.ollama-offline {
    background: #991b1b !important;
    color: #ffffff !important;
}
</style>
"""

# Configuração padrão do Ollama
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

# Configuração do Groq (primário)
GROQ_MODEL_DEFAULT = "llama-3.1-70b-versatile"
GROQ_MODELS = [
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]


def ollama_instalado() -> bool:
    """Verifica se o Ollama está instalado no sistema."""
    import shutil
    return shutil.which("ollama") is not None


def instalar_ollama():
    """Instala o Ollama via script oficial."""
    import subprocess
    
    with st.status("🔧 Instalando Ollama...", expanded=True) as status:
        st.write("📥 Baixando instalador...")
        
        try:
            # Usa o script oficial de instalação
            result = subprocess.run(
                ["curl", "-fsSL", "https://ollama.ai/install.sh"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                status.update(label="❌ Erro ao baixar", state="error")
                st.error(f"Erro: {result.stderr}")
                return False
            
            st.write("⚙️ Executando instalação...")
            
            # Executa o script de instalação
            install_result = subprocess.run(
                ["sh", "-c", result.stdout],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if install_result.returncode == 0:
                status.update(label="✅ Ollama instalado!", state="complete")
                st.write("✅ Instalação concluída!")
                return True
            else:
                status.update(label="❌ Erro na instalação", state="error")
                st.error(f"Erro: {install_result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            status.update(label="❌ Timeout", state="error")
            st.error("⏰ Tempo limite excedido. Tente novamente.")
            return False
        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error(f"Erro: {str(e)}")
            return False


def baixar_modelo_ollama(modelo: str = OLLAMA_MODEL):
    """Baixa um modelo do Ollama."""
    import subprocess
    
    with st.status(f"📦 Baixando modelo {modelo}...", expanded=True) as status:
        st.write(f"Este processo pode demorar alguns minutos...")
        
        try:
            result = subprocess.run(
                ["ollama", "pull", modelo],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos para modelos grandes
            )
            
            if result.returncode == 0:
                status.update(label=f"✅ Modelo {modelo} pronto!", state="complete")
                return True
            else:
                status.update(label="❌ Erro ao baixar modelo", state="error")
                st.error(f"Erro: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            status.update(label="❌ Timeout", state="error")
            st.error("⏰ Tempo limite. O modelo pode ser muito grande.")
            return False
        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error(f"Erro: {str(e)}")
            return False


def iniciar_ollama():
    """Instala (se necessário) e inicia o Ollama."""
    import subprocess
    import time
    
    # Passo 1: Verificar se está instalado
    if not ollama_instalado():
        st.info("🔧 Ollama não encontrado. Iniciando instalação...")
        
        if not instalar_ollama():
            return
        
        # Recarrega para atualizar PATH
        time.sleep(1)
    
    # Passo 2: Iniciar o serviço
    try:
        with st.spinner("🚀 Iniciando serviço Ollama..."):
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Aguarda o serviço iniciar
            time.sleep(3)
        
        if verificar_ollama():
            # Passo 3: Verificar se tem modelos
            modelos = listar_modelos_ollama()
            
            if not modelos:
                st.info(f"📦 Nenhum modelo encontrado. Baixando {OLLAMA_MODEL}...")
                if baixar_modelo_ollama(OLLAMA_MODEL):
                    st.success("✅ Tudo pronto! Ollama configurado.")
                    time.sleep(1)
                    st.rerun()
            else:
                st.success("✅ Ollama iniciado com sucesso!")
                time.sleep(1)
                st.rerun()
        else:
            st.warning("⏳ Ollama iniciando... Aguarde e atualize a página.")
            
    except FileNotFoundError:
        st.error("❌ Ollama ainda não está no PATH. Reinicie o terminal/aplicação.")
    except Exception as e:
        st.error(f"❌ Erro ao iniciar Ollama: {str(e)}")


def verificar_ollama() -> bool:
    """Verifica se o Ollama está rodando localmente."""
    try:
        import requests
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def listar_modelos_ollama() -> list:
    """Lista modelos disponíveis no Ollama."""
    try:
        import requests
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
    except Exception:
        pass
    return []


def obter_groq_api_key() -> str:
    """Obtém chave API do Groq de secrets ou variável de ambiente."""
    import os
    
    # Tenta pegar de secrets do Streamlit primeiro
    try:
        if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
            return st.secrets['GROQ_API_KEY']
    except Exception:
        pass
    
    # Fallback para variável de ambiente
    return os.getenv('GROQ_API_KEY', '')


def verificar_groq() -> bool:
    """Verifica se a API do Groq está configurada."""
    api_key = obter_groq_api_key()
    return bool(api_key and api_key.strip())


def gerar_resposta_groq(pergunta: str, contextos: list, modelo: str = GROQ_MODEL_DEFAULT) -> str:
    """
    Gera resposta usando Groq API (primário).
    """
    try:
        from langchain_groq import ChatGroq
        
        api_key = obter_groq_api_key()
        if not api_key:
            return "❌ Chave API do Groq não configurada."
        
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

        llm = ChatGroq(
            api_key=api_key,
            model=modelo,
            temperature=0.3,
            max_tokens=1024,
        )
        
        resposta = llm.invoke(prompt)
        return resposta.content.strip()
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta com Groq: {str(e)}"


def gerar_resposta_ollama(pergunta: str, contextos: list, modelo: str = OLLAMA_MODEL) -> str:
    """
    Gera resposta usando Ollama local (fallback secundário).
    """
    try:
        from langchain_ollama import OllamaLLM
        
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

        llm = OllamaLLM(model=modelo, base_url=OLLAMA_URL)
        resposta = llm.invoke(prompt)
        
        return resposta.strip()
        
    except Exception as e:
        return f"❌ Erro ao gerar resposta com Ollama: {str(e)}"


def gerar_resposta_sem_llm(pergunta: str, contextos: list) -> str:
    """Fallback quando Ollama não está disponível."""
    if not contextos:
        return "Não encontrei informações relevantes nos documentos para responder sua pergunta."
    
    resposta = "📚 **Trechos relevantes encontrados:**\n\n"
    
    for i, (doc, score) in enumerate(contextos, 1):
        trecho = doc.page_content.strip()
        fonte = doc.metadata.get("fonte", "Documento")
        resposta += f"**Trecho {i}** (de *{fonte}*):\n"
        resposta += f"> {trecho}\n\n"
    
    resposta += "---\n"
    resposta += "*ℹ️ Ollama não detectado. Para respostas elaboradas, inicie: `ollama serve`*"
    
    return resposta


def inicializar_sessao():
    """Inicializa variáveis de sessão do Streamlit."""
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []
    if "vectorstore" not in st.session_state:
        st.session_state.vectorstore = None
    if "fontes_ultima_resposta" not in st.session_state:
        st.session_state.fontes_ultima_resposta = []
    if "modo_llm" not in st.session_state:
        st.session_state.modo_llm = "auto"
    if "modelo_groq" not in st.session_state:
        st.session_state.modelo_groq = GROQ_MODEL_DEFAULT
    if "modelo_ollama" not in st.session_state:
        st.session_state.modelo_ollama = OLLAMA_MODEL


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
    
    with st.spinner(f"📄 Processando {arquivo_pdf.name}..."):
        chunks = processar_pdf_upload(arquivo_pdf.getvalue(), arquivo_pdf.name)
        
        if not chunks:
            st.error("❌ Não foi possível extrair texto do PDF.")
            return
        
        st.session_state.vectorstore = indexar_documentos(chunks, limpar_base=False)
        st.success(f"✅ {len(chunks)} trechos indexados de '{arquivo_pdf.name}'!")


def processar_pergunta(pergunta: str, modo_llm: str = "auto", modelo: str = None):
    """Processa pergunta do usuário e gera resposta.
    
    Args:
        pergunta: Pergunta do usuário
        modo_llm: "groq", "ollama", "sem_llm", ou "auto" (tenta Groq → Ollama → sem LLM)
        modelo: Nome do modelo (para Groq ou Ollama)
    """
    vectorstore = carregar_vectorstore()
    
    num_docs = contar_documentos(vectorstore)
    if num_docs == 0:
        return "⚠️ Nenhum documento indexado. Faça upload de um PDF primeiro!", []
    
    with st.spinner("🔍 Buscando informações relevantes..."):
        resultados = buscar_com_scores(pergunta, k=3, vectorstore=vectorstore)
    
    if not resultados:
        return "Não encontrei informações relevantes para sua pergunta.", []
    
    # Sistema de fallback inteligente
    if modo_llm == "auto":
        # Prioridade: Groq (rápido e grátis) → Ollama (local) → Sem LLM
        if verificar_groq():
            with st.spinner(f"⚡ Gerando resposta com Groq ({modelo or GROQ_MODEL_DEFAULT})..."):
                resposta = gerar_resposta_groq(pergunta, resultados, modelo or GROQ_MODEL_DEFAULT)
                if not resposta.startswith("❌"):
                    return resposta, resultados
        
        if verificar_ollama():
            with st.spinner(f"🦙 Gerando resposta com Ollama ({modelo or OLLAMA_MODEL})..."):
                resposta = gerar_resposta_ollama(pergunta, resultados, modelo or OLLAMA_MODEL)
                if not resposta.startswith("❌"):
                    return resposta, resultados
        
        # Fallback final: sem LLM
        return gerar_resposta_sem_llm(pergunta, resultados), resultados
    
    elif modo_llm == "groq" and verificar_groq():
        with st.spinner(f"⚡ Gerando resposta com Groq ({modelo or GROQ_MODEL_DEFAULT})..."):
            resposta = gerar_resposta_groq(pergunta, resultados, modelo or GROQ_MODEL_DEFAULT)
    
    elif modo_llm == "ollama" and verificar_ollama():
        with st.spinner(f"🦙 Gerando resposta com Ollama ({modelo or OLLAMA_MODEL})..."):
            resposta = gerar_resposta_ollama(pergunta, resultados, modelo or OLLAMA_MODEL)
    
    else:
        resposta = gerar_resposta_sem_llm(pergunta, resultados)
    
    return resposta, resultados


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


def render_app():
    """Função principal do chatbot."""
    
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    inicializar_sessao()
    
    st.title("🤖 Assistente Corporativo")
    st.markdown("Faça perguntas sobre seus documentos PDF usando **RAG** (Retrieval-Augmented Generation)")
    
    with st.container():
        st.markdown(
            """
            <div style="background:#f1f5f9; border-left:4px solid #8b5cf6; padding:1rem 1.25rem; border-radius:6px; margin-bottom:1.5rem;">
                <strong>O que é RAG?</strong><br>
                <em>Retrieval-Augmented Generation</em> combina busca semântica com geração de texto.
                O sistema encontra trechos relevantes nos seus documentos e usa como contexto para responder.<br><br>
                <strong>Como usar</strong><br>
                1. Faça upload de um PDF na barra lateral<br>
                2. Aguarde a indexação<br>
                3. Faça perguntas sobre o conteúdo!
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Documentos")
        
        arquivo_pdf = st.file_uploader("Upload PDF", type=["pdf"])
        
        if arquivo_pdf:
            if st.button("📤 Indexar documento", use_container_width=True):
                processar_upload(arquivo_pdf)
        
        st.markdown("---")
        
        vectorstore = carregar_vectorstore()
        num_docs = contar_documentos(vectorstore)
        
        st.subheader("📊 Status da Base")
        st.metric("Documentos indexados", num_docs)
        
        if num_docs > 0:
            st.markdown('<div class="status-card status-ok">✅ Pronto</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-card status-warning">⚠️ Base vazia</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Configuração de LLM
        st.subheader("🤖 Modelo de Linguagem")
        
        # Status dos provedores
        groq_disponivel = verificar_groq()
        ollama_disponivel = verificar_ollama()
        
        col1, col2 = st.columns(2)
        with col1:
            if groq_disponivel:
                st.markdown('<div class="ollama-status ollama-online">⚡ Groq OK</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ollama-status ollama-offline">⚡ Groq -</div>', unsafe_allow_html=True)
        with col2:
            if ollama_disponivel:
                st.markdown('<div class="ollama-status ollama-online">🦙 Ollama OK</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ollama-status ollama-offline">🦙 Ollama -</div>', unsafe_allow_html=True)
        
        st.markdown("")
        
        # Seletor de modo
        opcoes_modo = {
            "🎯 Automático (Groq → Ollama)": "auto",
            "⚡ Groq API (Cloud)": "groq",
            "🦙 Ollama (Local)": "ollama",
            "📚 Sem LLM (apenas chunks)": "sem_llm",
        }
        
        modo_label = st.selectbox(
            "Modo de resposta",
            options=list(opcoes_modo.keys()),
            index=0,
        )
        st.session_state.modo_llm = opcoes_modo[modo_label]
        
        # Configuração específica por modo
        if st.session_state.modo_llm in ["auto", "groq"]:
            if groq_disponivel:
                idx = GROQ_MODELS.index(st.session_state.modelo_groq) if st.session_state.modelo_groq in GROQ_MODELS else 0
                st.session_state.modelo_groq = st.selectbox(
                    "Modelo Groq",
                    GROQ_MODELS,
                    index=idx,
                    help="llama-3.1-70b é o mais capaz, 8b é o mais rápido"
                )
            else:
                st.info(
                    """
                    ⚡ **Groq não configurado**
                    
                    Para usar Groq (grátis e rápido):
                    1. Crie conta em [console.groq.com](https://console.groq.com)
                    2. Gere uma API key
                    3. Adicione ao `.streamlit/secrets.toml`:
                    ```toml
                    GROQ_API_KEY = "sua_chave_aqui"
                    ```
                    """
                )
        
        if st.session_state.modo_llm in ["auto", "ollama"]:
            if ollama_disponivel:
                modelos = listar_modelos_ollama()
                if modelos:
                    idx = modelos.index(st.session_state.modelo_ollama) if st.session_state.modelo_ollama in modelos else 0
                    st.session_state.modelo_ollama = st.selectbox("Modelo Ollama", modelos, index=idx)
            elif not eh_streamlit_cloud():
                st.caption("Ollama offline")
                if ollama_instalado():
                    btn_label = "🚀 Iniciar Ollama"
                else:
                    btn_label = "📥 Instalar Ollama"
                
                if st.button(btn_label, use_container_width=True, key="btn_start_ollama"):
                    iniciar_ollama()
        
        st.markdown("---")
        
        st.subheader("📚 Fontes")
        render_fontes(st.session_state.fontes_ultima_resposta)
        
        st.markdown("---")
        
        if st.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state.mensagens = []
            st.session_state.fontes_ultima_resposta = []
            st.rerun()
    
    # Chat
    st.markdown("---")
    render_chat()
    
    pergunta = st.chat_input("Digite sua pergunta sobre os documentos...")
    
    if pergunta:
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        
        # Determina qual modelo usar baseado no modo
        modelo_usado = None
        if st.session_state.modo_llm in ["auto", "groq"]:
            modelo_usado = st.session_state.modelo_groq
        elif st.session_state.modo_llm == "ollama":
            modelo_usado = st.session_state.modelo_ollama
        
        resposta, fontes = processar_pergunta(
            pergunta,
            modo_llm=st.session_state.modo_llm,
            modelo=modelo_usado
        )
        
        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        st.session_state.fontes_ultima_resposta = fontes
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align:center; color:#64748b; font-size:0.85rem;">
            Desenvolvido por <strong>Lenon de Paula</strong> · 
            <a href="mailto:lenondpaula@gmail.com" style="color:#3b82f6;">lenondpaula@gmail.com</a><br>
            <span style="font-size:0.75rem;">LangChain + ChromaDB + HuggingFace + Ollama</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="Assistente Corporativo RAG",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    render_app()
