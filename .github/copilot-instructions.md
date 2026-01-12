# Copilot Instructions - Hub de Criação

## Visão Geral da Arquitetura

Este é um **portfolio multi-aplicação** com Streamlit que hospeda 3+ apps de ML/NLP independentes em um único projeto. O arquivo [streamlit_app.py](../streamlit_app.py) serve como **homepage-índice**, enquanto cada app reside em `pages/` ou como submódulo próprio.

### Estrutura de Apps
- **App 1 (Previsão de Falhas)**: Manutenção preditiva com RandomForest → [pages/1_Previsao_Falhas.py](../pages/1_Previsao_Falhas.py)
- **App 2 (Análise de Sentimentos)**: NLP com TextBlob → [pages/2_Analise_Sentimentos.py](../pages/2_Analise_Sentimentos.py), módulo completo em [analise-sentimentos/](../analise-sentimentos/)
- **App 3 (Recomendação)**: SVD com Surprise → [pages/3_Que_tal_esse.py](../pages/3_Que_tal_esse.py), módulo em [sistema-recomendacao/](../sistema-recomendacao/)

## Convenções do Projeto

### Estrutura de Módulos Independentes
Cada app segue o padrão:
```
<nome-app>/
├── app/          # Dashboard principal (ex: dashboard.py, loja.py)
├── data/         # CSVs gerados/processados
├── src/          # Lógica de negócio (geração de dados, treino)
├── models/       # Modelos .pkl treinados
└── requirements.txt
```

### Sistema de Paths
**CRÍTICO**: Use `Path(__file__).resolve().parents[N]` para navegação:
- Apps em `pages/`: `parents[1]` para raiz, `parents[1] / "sistema-recomendacao"` para submódulos
- Apps em submódulos: `parents[1]` já está na raiz do submódulo
- Exemplo: [pages/3_Que_tal_esse.py#L9](../pages/3_Que_tal_esse.py#L9) importa de `sistema-recomendacao/app/`

### CSS Corporativo Consistente
Todos os apps compartilham o mesmo tema minimalista:
```python
CUSTOM_CSS = """<style>
:root {
    --primary: #0f172a;
    --accent: #3b82f6;
    --success: #22c55e;
    --danger: #ef4444;
}
"""
```
Ver [streamlit_app.py#L18-L100](../streamlit_app.py#L18-L100) para template completo.

## Workflows de Desenvolvimento

### 1. Treinar Modelo de Previsão de Falhas
```bash
python gerar_dados.py              # Gera data/raw/sensor_data.csv
python src/train_model.py          # Treina e salva models/modelo_preditivo.pkl
streamlit run pages/1_Previsao_Falhas.py
```

### 2. Setup Análise de Sentimentos
```bash
cd analise-sentimentos
python setup_nltk.py               # Download de recursos NLTK
python src/gerador_dados.py        # Gera dados sintéticos
python src/analise_motor.py        # Analisa sentimentos
# Execução via página do hub: streamlit run streamlit_app.py
```

### 3. Treinar Sistema de Recomendação
```bash
cd sistema-recomendacao
python src/gerar_dataset.py        # Cria produtos.csv e avaliacoes.csv
python src/treinar_modelo.py       # Treina SVD e salva models/recommender.pkl
```

### 4. Executar Hub Completo
```bash
streamlit run streamlit_app.py     # Homepage em http://localhost:8501
```

## Detalhes Técnicos Importantes

### Geração de Dados Sintéticos
Todos os apps usam **dados simulados** com Faker/NumPy para demonstração:
- **Sensores industriais**: [gerar_dados.py](../gerar_dados.py) - balanceamento de classes 30/70
- **Comentários sociais**: [analise-sentimentos/src/gerador_dados.py](../analise-sentimentos/src/gerador_dados.py)
- **Avaliações e-commerce**: [sistema-recomendacao/src/gerar_dataset.py](../sistema-recomendacao/src/gerar_dataset.py)

### Cache de Recursos
Use decoradores Streamlit para performance:
```python
@st.cache_data(show_spinner=False)  # Para DataFrames
def carregar_dados(): ...

@st.cache_resource(show_spinner=False)  # Para modelos
def carregar_modelo(): ...
```

### Integração NLTK
TextBlob requer downloads prévios - sempre inclua fallback:
```python
import nltk
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
```

### Constraints de Dependências
- `numpy<2.0` e `cython<3.0` por compatibilidade com scikit-surprise
- Ver [requirements.txt](../requirements.txt) na raiz para versões específicas

## Padrões de Código

### Imports de Submódulos
```python
# Em pages/X.py, para importar de submódulo:
APP_DIR = Path(__file__).resolve().parents[1] / "sistema-recomendacao" / "app"
sys.path.insert(0, str(APP_DIR))
from loja import render_app  # noqa: E402
```

### Modelos Scikit-learn
- Salvos com `joblib.dump()` em `models/`
- RandomForest com `class_weight="balanced"` para classes desbalanceadas
- Sempre imprima F1-score, não apenas acurácia

### Dashboard KPIs
Layout em cards HTML customizados com gradientes CSS:
```python
st.markdown(f'<div class="status-ok">✅ Sistema Saudável</div>', unsafe_allow_html=True)
```

## Detalhes dos Apps 4 e 5

### App 4: O Oráculo de Vendas (BI Preditivo com Prophet)

**Estrutura**:
```
oraculo-vendas/
├── app/
│   └── dashboard_vendas.py      # Dashboard principal com KPIs
├── data/
│   └── vendas_historico.csv     # 3 anos de histórico sintético (1096 dias)
├── models/
│   └── prophet_model.pkl         # Modelo Prophet treinado
├── src/
│   ├── gerar_vendas.py          # Geração de dados com tendência + sazonalidade
│   └── treinar_oraculo.py       # Treino do modelo Prophet
└── requirements.txt
```

**Workflow de Treino**:
```bash
cd oraculo-vendas
python src/gerar_vendas.py              # Gera data/vendas_historico.csv
python src/treinar_oraculo.py           # Treina e salva models/prophet_model.pkl
streamlit run ../pages/4_O_Oraculo_de_Vendas.py
```

**Características Técnicas**:
- **Dados sintéticos**: 3 anos de vendas diárias com padrões realistas:
  - Tendência linear (crescimento suave)
  - Sazonalidade multiplicativa (7 dias, 365 dias)
  - Pico de Black Friday (~40% acima da média)
  - Ruído gaussiano (±5%)
- **Configuração Prophet**:
  - `interval_width=0.95` para intervalos de confiança (IC 95%)
  - Multiplicative seasonality (mais realista para dados de vendas)
  - Feriados brasileiros registrados (e.g., Black Friday em Nov)
  - `yearly_seasonality=True`, `weekly_seasonality=True`, `daily_seasonality=False`
- **Dashboard**:
  - KPIs: Próximo mês estimado, variação vs histórico, confiabilidade IC
  - Gráficos Plotly: Série histórica + forecast, decomposição de componentes, resíduos
  - Export: CSV com forecast (com IC inferior/superior) e parâmetros do modelo
  - Slider para ajustar períodos de forecast (7 a 90 dias)

**Imports Críticos**:
```python
from prophet import Prophet
from pathlib import Path
import joblib
import plotly.graph_objects as go
```

**Checklist de Deploy**:
- [ ] Dados gerados com seed=42 para reproducibilidade
- [ ] Modelo pickleado em `models/prophet_model.pkl`
- [ ] CSS corporativo aplicado no dashboard
- [ ] Cache Streamlit para dados (`@st.cache_data`)
- [ ] Conversor de forecast DataFrame para CSV

---

### App 5: O Assistente Corporativo (RAG com Ollama)

**Estrutura**:
```
assistente-rag/
├── app/
│   └── chatbot_rag.py               # Interface RAG + Ollama
├── data/
│   └── (PDFs do usuário)
├── src/
│   ├── processador_pdf.py           # Extração de texto com PyPDF
│   └── indexador.py                 # Indexação ChromaDB
├── models/
│   └── (ChromaDB vectors)
└── requirements.txt
```

**Workflow de Setup**:
```bash
cd assistente-rag
# Local: Instalar Ollama manualmente (https://ollama.ai)
ollama pull llama3.2                 # ~2.3GB

# Streamlit Cloud: Automático via detectar_streamlit_cloud()
streamlit run ../pages/5_O_Assistente_Corporativo.py
```

**Arquitetura RAG**:
1. **Ingestão (PDF)**:
   - PyPDF2 extrai texto bruto de PDFs
   - RecursiveCharacterTextSplitter divide em chunks (600 chars, 200 overlap)
   - Embedding: sentence-transformers/all-MiniLM-L6-v2 (384-dim, CPU)

2. **Indexação (ChromaDB)**:
   - Vector store em disco (`chroma_vectordb/`)
   - Similaridade cosine para recuperação
   - Scoring automático per chunk (0-1)

3. **Geração (Ollama LLM)**:
   - Endpoint local: `http://localhost:11434`
   - Modelo default: `llama3.2` (Ollama auto-seleciona)
   - Context window: até 2048 tokens
   - Temperature: 0.7 (balanceado)

**Funções Principais** (em `chatbot_rag.py`):
```python
def detectar_streamlit_cloud() -> bool:
    """Detecta se está rodando em Streamlit Cloud"""
    return os.getenv("STREAMLIT_SERVER_HEADLESS") == "true"

def verificar_ollama() -> bool:
    """Verifica se Ollama está instalado e rodando"""
    # shutil.which("ollama") + HTTP health check em :11434

def listar_modelos_ollama() -> list[str]:
    """List: GET /api/tags"""

def instalar_ollama_cloud() -> bool:
    """subprocess + apt para Cloud (detecta ubuntu/debian)"""

def gerar_resposta_ollama(prompt: str, contexto: str) -> str:
    """LLM inference com contexto do RAG"""
```

**Imports Críticos** (v0.3+ LangChain):
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama
```

**Comportamento Offline**:
- Ollama offline → Mostra chunks relevantes do PDF (fallback gracioso)
- Interrupção de conexão → Tenta reconectar, depois fallback
- Streamlit Cloud sem Docker → Oferece botão "📥 Instalar Ollama"

**Checklist de Deploy**:
- [ ] ChromaDB persiste em `chroma_vectordb/` na raiz do submódulo
- [ ] Ollama health check em `/proc/pid` ou HTTP
- [ ] Environment detection para Streamlit Cloud
- [ ] Auto-install subprocess com quoting seguro
- [ ] Cache Streamlit para embeddings (`@st.cache_resource`)
- [ ] Tratamento de PDFs inválidos/vazio
- [ ] Sidebar com upload + histórico de chat

**Notas para Streamlit Cloud**:
- Ollama requer Docker ou sistema Unix (WSL em Windows)
- Instalação via apt-get em primeiro boot (~5-10 min)
- Modelo `llama3.2` baixa ~2.3GB (cache via `/root/.ollama`)
- Recursos: ~2GB RAM + 500MB CPU suficientes para llama3.2

## Como Adicionar um Novo App ao Hub

### Opção 1: App Simples (Tudo em `pages/`)
Para apps autocontidos sem módulos complexos:

1. **Criar página em `pages/`**:
   ```python
   # pages/4_Novo_App.py
   from pathlib import Path
   import streamlit as st
   
   MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "novo_modelo.pkl"
   DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "novo_dataset.csv"
   ```

2. **Adicionar CSS padrão**: Copie o bloco `CUSTOM_CSS` de [pages/1_Previsao_Falhas.py#L12-L74](../pages/1_Previsao_Falhas.py#L12-L74)

3. **Registrar no hub**: Adicione entrada em `streamlit_app.py`:
   ```python
   APPS = [
       # ... apps existentes ...
       {
           "title": "📈 App 4 — Novo App",
           "desc": "Descrição concisa do que o app faz.",
           "status": "active",  # ou "dev"
           "page": "pages/4_Novo_App",
       },
   ]
   ```

### Opção 2: App Modular (Com Submódulo)
Para apps com lógica complexa ou múltiplos arquivos:

1. **Criar estrutura de submódulo**:
   ```bash
   mkdir -p novo-app/{app,data,models,src}
   touch novo-app/requirements.txt
   ```

2. **Implementar lógica no submódulo**:
   ```python
   # novo-app/app/dashboard.py
   from pathlib import Path
   
   BASE_DIR = Path(__file__).resolve().parents[1]
   
   def render_app():
       st.title("Novo App")
       # Lógica do dashboard aqui
   ```

3. **Criar página ponte em `pages/`**:
   ```python
   # pages/4_Novo_App.py
   from pathlib import Path
   import sys
   import streamlit as st
   
   APP_DIR = Path(__file__).resolve().parents[1] / "novo-app" / "app"
   sys.path.insert(0, str(APP_DIR))
   from dashboard import render_app  # noqa: E402
   
   st.set_page_config(page_title="Novo App", page_icon="📈", layout="wide")
   render_app()
   ```

4. **Adicionar scripts auxiliares**:
   - `novo-app/src/gerar_dados.py` - Geração de dados sintéticos
   - `novo-app/src/treinar_modelo.py` - Treino de modelos
   - `novo-app/requirements.txt` - Dependências específicas

5. **Registrar no hub** (mesmo processo da Opção 1)

### Checklist de Qualidade
- [ ] CSS corporativo aplicado (cores, cards, badges)
- [ ] Cache Streamlit configurado (`@st.cache_data`, `@st.cache_resource`)
- [ ] Paths relativos usando `Path(__file__).resolve().parents[N]`
- [ ] Dados sintéticos gerados com seed fixo (`random.seed(42)`)
- [ ] Modelos salvos em `models/*.pkl` com `joblib`
- [ ] Status badge correto no hub ("active" ou "dev")
- [ ] README específico em `<submódulo>/README.md` (se aplicável)

## Deploy no Streamlit Cloud

- **Entrypoint**: `streamlit_app.py` (definir no painel do Streamlit Cloud)
- **Python Version**: Especificado em [runtime.txt](../runtime.txt)
- **Recursos NLTK**: Rodar `analise-sentimentos/setup_nltk.py` no primeiro boot (adicionar ao script de inicialização se necessário)
