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
