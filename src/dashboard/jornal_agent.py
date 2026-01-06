"""
Jornal-Agent Dashboard - Configuração e Monitoramento.

Dashboard corporativa e minimalista para:
- Configurar credenciais e tokens
- Monitorar execuções
- Executar o agente manualmente
"""

import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import subprocess
import sys

# Configuração da página
st.set_page_config(
    page_title="Jornal-Agent | Configurações",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Customizado - Design Corporativo Minimalista
st.markdown("""
<style>
    /* Reset e variáveis */
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
    
    /* Fundo principal */
    .stApp {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-card);
        border-right: 1px solid var(--border);
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: var(--text);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: var(--text) !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 2rem !important;
        letter-spacing: -0.5px;
    }
    
    /* Cards/Containers */
    .config-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .config-card h3 {
        margin-top: 0;
        margin-bottom: 1rem;
        font-size: 1.1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-success {
        background: rgba(0, 210, 106, 0.15);
        color: var(--success);
        border: 1px solid rgba(0, 210, 106, 0.3);
    }
    
    .status-warning {
        background: rgba(255, 193, 7, 0.15);
        color: var(--warning);
        border: 1px solid rgba(255, 193, 7, 0.3);
    }
    
    .status-error {
        background: rgba(233, 69, 96, 0.15);
        color: var(--highlight);
        border: 1px solid rgba(233, 69, 96, 0.3);
    }
    
    /* Input fields */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background: var(--secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: var(--highlight) !important;
        box-shadow: 0 0 0 1px var(--highlight) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--highlight) 0%, #c23a51 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
    }
    
    /* Secondary button style */
    .secondary-btn > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }
    
    .secondary-btn > button:hover {
        background: var(--accent) !important;
        border-color: var(--accent) !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 1.8rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        color: var(--text) !important;
    }
    
    /* Divider */
    hr {
        border-color: var(--border) !important;
    }
    
    /* Toast/Alert */
    .stAlert {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 8px;
        color: var(--text-muted);
        padding: 8px 16px;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--accent) !important;
        color: var(--text) !important;
        border-color: var(--accent) !important;
    }
    
    /* Info text */
    .info-text {
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-top: 0.25rem;
    }
    
    /* Logo area */
    .logo-container {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    
    .logo-container h1 {
        font-size: 1.5rem !important;
        margin: 0;
    }
    
    .logo-container p {
        color: var(--text-muted);
        font-size: 0.9rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# Paths
BASE_DIR = Path(__file__).parent.parent.parent
CONFIG_FILE = BASE_DIR / "config" / "settings.json"
OUTPUT_DIR = BASE_DIR / "output"


def load_config() -> dict:
    """Carrega configurações salvas."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except:
            pass
    return {}


def save_config(config: dict) -> bool:
    """Salva configurações."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False


def get_last_run_status() -> dict:
    """Obtém status da última execução."""
    status_file = OUTPUT_DIR / "last-run-status.json"
    if status_file.exists():
        try:
            return json.loads(status_file.read_text())
        except:
            pass
    return {}


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mascara um segredo para exibição."""
    if not value or len(value) <= show_chars:
        return "••••••••"
    return value[:show_chars] + "•" * (len(value) - show_chars)


def render_status_badge(success: bool, label: str = None) -> str:
    """Renderiza badge de status."""
    if success:
        icon = "✓"
        cls = "status-success"
        text = label or "Configurado"
    else:
        icon = "○"
        cls = "status-warning"
        text = label or "Pendente"
    return f'<span class="status-badge {cls}">{icon} {text}</span>'


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <h1>📰 Jornal-Agent</h1>
        <p>Painel de Configurações</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Menu de navegação
    page = st.radio(
        "Navegação",
        ["⚙️ Configurações", "📊 Monitoramento", "▶️ Execução", "📖 Documentação"],
        label_visibility="collapsed",
    )
    
    st.divider()
    
    # Status rápido
    status = get_last_run_status()
    if status:
        st.markdown("### Status")
        
        if status.get("success"):
            st.markdown(render_status_badge(True, "Última execução OK"), unsafe_allow_html=True)
        else:
            st.markdown(render_status_badge(False, "Falha na execução"), unsafe_allow_html=True)
        
        if status.get("timestamp"):
            try:
                dt = datetime.fromisoformat(status["timestamp"])
                st.caption(f"📅 {dt.strftime('%d/%m/%Y %H:%M')}")
            except:
                pass
    
    st.divider()
    
    # Versão
    st.caption("v1.0.0 | © 2026")


# ============================================================================
# PÁGINA: CONFIGURAÇÕES
# ============================================================================
if page == "⚙️ Configurações":
    st.title("Configurações")
    st.markdown("Configure as credenciais e tokens necessários para o funcionamento do agente.")
    
    # Carrega config existente
    config = load_config()
    
    # Tabs para organizar configurações
    tab1, tab2, tab3, tab4 = st.tabs(["🔐 Jornal", "🤖 LLM / IA", "📱 WhatsApp", "📧 E-mail"])
    
    # ---------- TAB: JORNAL ----------
    with tab1:
        st.markdown("#### Credenciais do Jornal")
        st.markdown('<p class="info-text">Configure o acesso à área restrita do jornal para download do PDF.</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            jornal_user = st.text_input(
                "Usuário",
                value=config.get("jornal_user", ""),
                placeholder="seu_usuario",
                key="jornal_user",
            )
        
        with col2:
            jornal_pass = st.text_input(
                "Senha",
                value=config.get("jornal_pass", ""),
                type="password",
                placeholder="••••••••",
                key="jornal_pass",
            )
        
        st.markdown("#### URLs de Acesso")
        
        jornal_login_url = st.text_input(
            "URL de Login",
            value=config.get("jornal_login_url", "https://exemplo-jornal.com.br/login"),
            placeholder="https://jornal.com.br/login",
            key="jornal_login_url",
        )
        
        jornal_pdf_url = st.text_input(
            "URL da Página do PDF",
            value=config.get("jornal_pdf_url", "https://exemplo-jornal.com.br/assinante/edicao"),
            placeholder="https://jornal.com.br/assinante/edicao",
            key="jornal_pdf_url",
        )
    
    # ---------- TAB: LLM ----------
    with tab2:
        st.markdown("#### Configuração do LLM")
        st.markdown('<p class="info-text">Configure a API de inteligência artificial para geração de resumos.</p>', unsafe_allow_html=True)
        
        llm_provider = st.selectbox(
            "Provedor",
            ["OpenAI", "DeepSeek", "Outro (compatível OpenAI)"],
            index=["OpenAI", "DeepSeek", "Outro (compatível OpenAI)"].index(
                config.get("llm_provider", "OpenAI")
            ) if config.get("llm_provider") in ["OpenAI", "DeepSeek", "Outro (compatível OpenAI)"] else 0,
            key="llm_provider",
        )
        
        llm_api_key = st.text_input(
            "API Key",
            value=config.get("llm_api_key", ""),
            type="password",
            placeholder="sk-...",
            key="llm_api_key",
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if llm_provider == "OpenAI":
                default_model = "gpt-4o-mini"
                models = ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            elif llm_provider == "DeepSeek":
                default_model = "deepseek-chat"
                models = ["deepseek-chat", "deepseek-coder"]
            else:
                default_model = config.get("llm_model", "")
                models = None
            
            if models:
                llm_model = st.selectbox(
                    "Modelo",
                    models,
                    index=models.index(config.get("llm_model", default_model)) if config.get("llm_model") in models else 0,
                    key="llm_model",
                )
            else:
                llm_model = st.text_input(
                    "Modelo",
                    value=config.get("llm_model", ""),
                    placeholder="nome-do-modelo",
                    key="llm_model_custom",
                )
        
        with col2:
            if llm_provider == "DeepSeek":
                default_url = "https://api.deepseek.com/v1"
            elif llm_provider == "Outro (compatível OpenAI)":
                default_url = config.get("llm_base_url", "")
            else:
                default_url = ""
            
            llm_base_url = st.text_input(
                "URL Base (opcional)",
                value=config.get("llm_base_url", default_url),
                placeholder="https://api.exemplo.com/v1",
                key="llm_base_url",
                disabled=(llm_provider == "OpenAI"),
            )
    
    # ---------- TAB: WHATSAPP ----------
    with tab3:
        st.markdown("#### WhatsApp Cloud API")
        st.markdown('<p class="info-text">Configure o envio de mensagens via WhatsApp Business.</p>', unsafe_allow_html=True)
        
        whatsapp_token = st.text_input(
            "Access Token",
            value=config.get("whatsapp_token", ""),
            type="password",
            placeholder="EAAxxxxxxx...",
            key="whatsapp_token",
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            whatsapp_phone_id = st.text_input(
                "Phone Number ID",
                value=config.get("whatsapp_phone_id", ""),
                placeholder="1234567890",
                key="whatsapp_phone_id",
            )
        
        with col2:
            whatsapp_recipient = st.text_input(
                "Número do Destinatário",
                value=config.get("whatsapp_recipient", ""),
                placeholder="5511999999999",
                key="whatsapp_recipient",
                help="Formato: código do país + DDD + número",
            )
        
        with st.expander("ℹ️ Como obter as credenciais"):
            st.markdown("""
            1. Acesse [Meta for Developers](https://developers.facebook.com)
            2. Crie um App do tipo "Business"
            3. Adicione o produto "WhatsApp"
            4. Em **WhatsApp → API Setup**:
               - Copie o **Phone number ID**
               - Gere um **Access Token** permanente
            5. Adicione números de teste na lista de permitidos
            """)
    
    # ---------- TAB: EMAIL ----------
    with tab4:
        st.markdown("#### Configuração SMTP (Fallback)")
        st.markdown('<p class="info-text">Configure o envio por e-mail quando o WhatsApp falhar.</p>', unsafe_allow_html=True)
        
        smtp_enabled = st.toggle(
            "Ativar fallback por e-mail",
            value=config.get("smtp_enabled", False),
            key="smtp_enabled",
        )
        
        if smtp_enabled:
            col1, col2 = st.columns(2)
            
            with col1:
                smtp_host = st.text_input(
                    "Servidor SMTP",
                    value=config.get("smtp_host", "smtp.gmail.com"),
                    placeholder="smtp.gmail.com",
                    key="smtp_host",
                )
                
                smtp_user = st.text_input(
                    "Usuário",
                    value=config.get("smtp_user", ""),
                    placeholder="seu@email.com",
                    key="smtp_user",
                )
                
                email_from = st.text_input(
                    "E-mail Remetente",
                    value=config.get("email_from", ""),
                    placeholder="noreply@empresa.com",
                    key="email_from",
                )
            
            with col2:
                smtp_port = st.number_input(
                    "Porta",
                    value=config.get("smtp_port", 587),
                    min_value=1,
                    max_value=65535,
                    key="smtp_port",
                )
                
                smtp_pass = st.text_input(
                    "Senha",
                    value=config.get("smtp_pass", ""),
                    type="password",
                    placeholder="••••••••",
                    key="smtp_pass",
                )
                
                email_to = st.text_input(
                    "E-mail Destinatário",
                    value=config.get("email_to", ""),
                    placeholder="destinatario@empresa.com",
                    key="email_to",
                )
    
    # ---------- SALVAR ----------
    st.divider()
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("💾 Salvar Configurações", type="primary", use_container_width=True):
            new_config = {
                # Jornal
                "jornal_user": jornal_user,
                "jornal_pass": jornal_pass,
                "jornal_login_url": jornal_login_url,
                "jornal_pdf_url": jornal_pdf_url,
                # LLM
                "llm_provider": llm_provider,
                "llm_api_key": llm_api_key,
                "llm_model": llm_model if models else st.session_state.get("llm_model_custom", ""),
                "llm_base_url": llm_base_url if llm_provider != "OpenAI" else "",
                # WhatsApp
                "whatsapp_token": whatsapp_token,
                "whatsapp_phone_id": whatsapp_phone_id,
                "whatsapp_recipient": whatsapp_recipient,
                # SMTP
                "smtp_enabled": smtp_enabled,
            }
            
            if smtp_enabled:
                new_config.update({
                    "smtp_host": smtp_host,
                    "smtp_port": smtp_port,
                    "smtp_user": smtp_user,
                    "smtp_pass": smtp_pass,
                    "email_from": email_from,
                    "email_to": email_to,
                })
            
            if save_config(new_config):
                st.success("✅ Configurações salvas com sucesso!")
                st.balloons()
    
    with col2:
        if st.button("🔄 Exportar .env", use_container_width=True):
            env_content = f"""# Gerado pela Dashboard em {datetime.now().strftime('%Y-%m-%d %H:%M')}
JORNAL_USER={jornal_user}
JORNAL_PASS={jornal_pass}
JORNAL_LOGIN_URL={jornal_login_url}
JORNAL_PDF_URL={jornal_pdf_url}
LLM_API_KEY={llm_api_key}
LLM_MODEL={llm_model if models else st.session_state.get("llm_model_custom", "")}
LLM_BASE_URL={llm_base_url if llm_provider != "OpenAI" else ""}
WHATSAPP_TOKEN={whatsapp_token}
WHATSAPP_PHONE_ID={whatsapp_phone_id}
WHATSAPP_RECIPIENT={whatsapp_recipient}
"""
            if smtp_enabled:
                env_content += f"""SMTP_HOST={smtp_host}
SMTP_PORT={smtp_port}
SMTP_USER={smtp_user}
SMTP_PASS={smtp_pass}
EMAIL_FROM={email_from}
EMAIL_TO={email_to}
"""
            st.download_button(
                "📥 Download .env",
                env_content,
                file_name=".env",
                mime="text/plain",
            )
    
    with col3:
        st.markdown('<div class="secondary-btn">', unsafe_allow_html=True)
        if st.button("🗑️ Limpar", use_container_width=True):
            if CONFIG_FILE.exists():
                CONFIG_FILE.unlink()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================================
# PÁGINA: MONITORAMENTO
# ============================================================================
elif page == "📊 Monitoramento":
    st.title("Monitoramento")
    st.markdown("Acompanhe o status e histórico de execuções do agente.")
    
    # Status atual
    status = get_last_run_status()
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        success = status.get("success", False)
        st.metric(
            "Status",
            "✅ OK" if success else "❌ Erro" if status else "⏸️ Nunca executado",
        )
    
    with col2:
        phases = status.get("phases", {})
        total_phases = len(phases)
        success_phases = sum(1 for p in phases.values() if p.get("success"))
        st.metric("Fases", f"{success_phases}/{total_phases}" if phases else "—")
    
    with col3:
        processing = phases.get("processing", {})
        st.metric("Páginas", processing.get("total_pages", "—"))
    
    with col4:
        st.metric("Itens", processing.get("total_items", "—"))
    
    st.divider()
    
    # Detalhes da última execução
    if status:
        st.markdown("### Última Execução")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Fases")
            for phase_name, phase_data in status.get("phases", {}).items():
                phase_success = phase_data.get("success", False)
                icon = "✅" if phase_success else "❌"
                st.markdown(f"{icon} **{phase_name.title()}**")
                
                # Detalhes da fase
                for key, value in phase_data.items():
                    if key != "success":
                        st.caption(f"  └ {key}: {value}")
        
        with col2:
            st.markdown("#### Informações")
            
            if status.get("timestamp"):
                st.markdown(f"📅 **Data/Hora:** {status['timestamp'][:19].replace('T', ' ')}")
            
            if status.get("dry_run"):
                st.markdown("🧪 **Modo:** Dry-run (teste)")
            else:
                st.markdown("🚀 **Modo:** Produção")
            
            if status.get("error"):
                st.error(f"**Erro:** {status['error']}")
    
    st.divider()
    
    # Arquivos de saída
    st.markdown("### Arquivos Gerados")
    
    if OUTPUT_DIR.exists():
        files = list(OUTPUT_DIR.glob("*"))
        files = [f for f in files if f.is_file() and not f.name.startswith(".")]
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        if files:
            for f in files[:10]:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    icon = "📄" if f.suffix == ".txt" else "📊" if f.suffix == ".json" else "📝"
                    st.markdown(f"{icon} `{f.name}`")
                
                with col2:
                    size = f.stat().st_size
                    if size < 1024:
                        st.caption(f"{size} B")
                    else:
                        st.caption(f"{size/1024:.1f} KB")
                
                with col3:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    st.caption(mtime.strftime("%d/%m %H:%M"))
        else:
            st.info("Nenhum arquivo gerado ainda.")
    else:
        st.info("Diretório de saída não encontrado.")


# ============================================================================
# PÁGINA: EXECUÇÃO
# ============================================================================
elif page == "▶️ Execução":
    st.title("Execução Manual")
    st.markdown("Execute o agente manualmente para testes ou execuções avulsas.")
    
    # Opções
    col1, col2 = st.columns(2)
    
    with col1:
        dry_run = st.toggle(
            "🧪 Modo Dry-Run (teste)",
            value=True,
            help="Simula a execução sem enviar mensagens reais",
        )
    
    with col2:
        verbose = st.toggle(
            "📝 Logs detalhados",
            value=False,
        )
    
    st.divider()
    
    # Verificação de configurações
    config = load_config()
    
    st.markdown("### Pré-requisitos")
    
    checks = [
        ("Credenciais do Jornal", bool(config.get("jornal_user") and config.get("jornal_pass"))),
        ("API Key do LLM", bool(config.get("llm_api_key"))),
        ("WhatsApp configurado", bool(config.get("whatsapp_token") and config.get("whatsapp_phone_id"))),
    ]
    
    all_ok = True
    for name, ok in checks:
        if ok:
            st.markdown(f"✅ {name}")
        else:
            st.markdown(f"⚠️ {name} - *Não configurado*")
            if not dry_run:
                all_ok = False
    
    st.divider()
    
    # Botão de execução
    if dry_run or all_ok:
        if st.button("▶️ Executar Agente", type="primary", use_container_width=True):
            with st.spinner("Executando..."):
                # Prepara comando
                cmd = [sys.executable, "-m", "src.main"]
                if dry_run:
                    cmd.append("--dry-run")
                if verbose:
                    cmd.append("--verbose")
                
                # Executa
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=str(BASE_DIR),
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    
                    if result.returncode == 0:
                        st.success("✅ Execução concluída com sucesso!")
                    else:
                        st.error("❌ Execução falhou")
                    
                    # Mostra logs
                    with st.expander("📋 Logs de execução", expanded=True):
                        st.code(result.stdout + result.stderr, language="log")
                    
                except subprocess.TimeoutExpired:
                    st.error("⏰ Timeout: execução demorou mais de 5 minutos")
                except Exception as e:
                    st.error(f"Erro: {e}")
    else:
        st.warning("⚠️ Configure todas as credenciais antes de executar em modo produção.")
        st.info("Você pode usar o modo **Dry-Run** para testar sem credenciais.")


# ============================================================================
# PÁGINA: DOCUMENTAÇÃO
# ============================================================================
elif page == "📖 Documentação":
    st.title("Documentação")
    
    st.markdown("""
    ### 📰 Sobre o Jornal-Agent
    
    O Jornal-Agent é um sistema automatizado para:
    
    1. **Download** - Acessa a área restrita do jornal e baixa o PDF diário
    2. **Processamento** - Extrai texto das páginas (com OCR quando necessário)
    3. **Clipagem** - Gera resumos inteligentes usando IA
    4. **Envio** - Envia o PDF e resumo via WhatsApp
    
    ---
    
    ### 🔧 Configuração Rápida
    
    1. Acesse a aba **Configurações**
    2. Preencha as credenciais do jornal
    3. Configure a API Key do LLM (OpenAI ou DeepSeek)
    4. Configure o WhatsApp Cloud API
    5. Salve as configurações
    
    ---
    
    ### ⏰ Execução Automática
    
    O agente executa automaticamente via GitHub Actions:
    - **Horário**: 06:00 BRT (09:00 UTC)
    - **Frequência**: Diariamente
    
    Para configurar, adicione os secrets no GitHub:
    - `JORNAL_USER`
    - `JORNAL_PASS`
    - `LLM_API_KEY`
    - `WHATSAPP_TOKEN`
    - `WHATSAPP_PHONE_ID`
    
    ---
    
    ### 📱 WhatsApp Cloud API
    
    Para enviar mensagens via WhatsApp:
    
    1. Crie conta no [Meta for Developers](https://developers.facebook.com)
    2. Crie um App do tipo "Business"
    3. Adicione o produto WhatsApp
    4. Obtenha o Phone Number ID e Access Token
    5. Adicione números de teste
    
    ---
    
    ### 🤖 LLMs Suportados
    
    | Provedor | Modelos |
    |----------|---------|
    | OpenAI | gpt-4o-mini, gpt-4o, gpt-4-turbo |
    | DeepSeek | deepseek-chat, deepseek-coder |
    | Outros | Qualquer API compatível com OpenAI |
    
    ---
    
    ### ❓ Suporte
    
    Em caso de dúvidas ou problemas:
    - Verifique os logs em `output/jornal-agent.log`
    - Revise o arquivo `output/last-run-status.json`
    - Execute em modo dry-run para diagnóstico
    """)
