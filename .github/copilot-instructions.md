# Copilot Instructions - Hub de Criação

Portfolio multi-aplicação Streamlit com 8 apps de ML/NLP independentes. O `streamlit_app.py` serve como homepage-índice.

## Arquitetura

### Padrão de Submódulos
Cada app possui estrutura isolada:
```
<nome-app>/
├── app/          # Dashboard (render_app())
├── data/         # CSVs gerados
├── src/          # Geração de dados + treino
└── models/       # Modelos .pkl
```

**Páginas ponte** em `pages/` importam via:
```python
APP_DIR = Path(__file__).resolve().parents[1] / "sistema-recomendacao" / "app"
sys.path.insert(0, str(APP_DIR))
from loja import render_app  # noqa: E402
```

### Apps Ativos
| App | Stack | Submódulo |
|-----|-------|-----------|
| 1 - Precaução Mecânica | RandomForest, joblib | `src/train_model.py` |
| 2 - Reputação de Marca | TextBlob, NLTK | `analise-sentimentos/` |
| 3 - Sugestão de Compra | SVD (Surprise) | `sistema-recomendacao/` |
| 4 - Oráculo de Vendas | Prophet | `oraculo-vendas/` |
| 5 - Assistente RAG | LangChain, ChromaDB, Groq/Ollama | `assistente-rag/` |
| 6 - GIG-Master AI | Otimização greedy, Plotly | `projeto-gig-master/` |
| 7 - Burger-Flow Intelligence | Prophet, Clustering BCG, Plotly | `projeto-burger-flow/` |
| 8 - PoA-Insight Explorer | Folium, streamlit-folium, geopy | `projeto-poa-explorer/` |

## Workflows Essenciais

```bash
# Hub completo
streamlit run streamlit_app.py

# Treinar modelos (cada app)
python gerar_dados.py && python src/train_model.py          # App 1
cd sistema-recomendacao && python src/gerar_dataset.py && python src/treinar_modelo.py  # App 3
cd oraculo-vendas && python src/gerar_vendas.py && python src/treinar_oraculo.py        # App 4
cd projeto-gig-master && python src/gerar_mercado.py && python src/motor_logistica.py   # App 6
cd projeto-burger-flow && python src/gerar_dados_burger.py && python src/previsao_estoque.py  # App 7
cd projeto-poa-explorer && python src/gerar_locais_poa.py                                    # App 8
```

## Convenções Críticas

### Paths (OBRIGATÓRIO)
```python
BASE_DIR = Path(__file__).resolve().parents[1]  # Sobe 1 nível para submódulo
MODEL_PATH = BASE_DIR / "models" / "modelo.pkl"
```

### CSS Corporativo
Todas as páginas usam `CUSTOM_CSS` com variáveis:
- `--primary: #0f172a`, `--accent: #3b82f6`, `--success: #22c55e`, `--danger: #ef4444`

### Cache Streamlit
```python
@st.cache_data(show_spinner=False)     # DataFrames
@st.cache_resource(show_spinner=False)  # Modelos
```

### Dados Sintéticos
Sempre use `seed=42` para reprodutibilidade (NumPy, Faker, random).

## Dependências Especiais

- `numpy<2.0`, `cython<3.0` — compatibilidade scikit-surprise
- App 5: Groq API (Cloud) ou Ollama (local) com fallback automático

## Adicionar Novo App

1. Criar submódulo em `<nome>/` com estrutura padrão
2. Criar página ponte em `pages/N_Nome_App.py`
3. Registrar em `APPS` no `streamlit_app.py`

Ver exemplos: [pages/5_O_Assistente_Corporativo.py](pages/5_O_Assistente_Corporativo.py), [pages/6_GIG_Master_AI.py](pages/6_GIG_Master_AI.py)
