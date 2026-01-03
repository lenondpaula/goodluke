# 📊 Analista de Marca - Análise de Sentimentos

Sistema de monitoramento de reputação de marca baseado em análise de sentimentos de comentários em redes sociais.

## 🎯 Sobre o Projeto

O **Analista de Marca** é uma aplicação que utiliza Processamento de Linguagem Natural (NLP) para analisar o sentimento de menções em redes sociais sobre a marca fictícia **TechNova**.

### Funcionalidades

- ✅ Geração de dados sintéticos de comentários de redes sociais
- ✅ Análise de sentimentos usando TextBlob (Positivo, Negativo, Neutro)
- ✅ Dashboard interativo com KPIs e gráficos
- ✅ Filtros por plataforma, classificação e período
- ✅ Exportação de dados analisados

## 🚀 Instalação

### 1. Instalar dependências

```bash
cd analise-sentimentos
pip install -r requirements.txt
```

### 2. Configurar NLTK

```bash
python setup_nltk.py
```

## 📁 Estrutura do Projeto

```
analise-sentimentos/
├── app/
│   └── dashboard.py       # Dashboard Streamlit
├── data/
│   ├── comentarios_social.csv        # Dados brutos gerados
│   └── comentarios_classificados.csv # Dados com análise
├── src/
│   ├── gerador_dados.py   # Gerador de dados sintéticos
│   └── analise_motor.py   # Motor de análise de sentimentos
├── requirements.txt       # Dependências Python
├── setup_nltk.py         # Setup do NLTK
└── README.md
```

## 🔧 Como Usar

### Passo 1: Gerar Dados Sintéticos

```bash
cd analise-sentimentos
python src/gerador_dados.py
```

Isso criará 500 comentários simulados em `data/comentarios_social.csv`.

### Passo 2: Executar Análise de Sentimentos

```bash
python src/analise_motor.py
```

Isso analisará os comentários e salvará em `data/comentarios_classificados.csv`.

### Passo 3: Iniciar o Dashboard

```bash
streamlit run app/dashboard.py
```

O dashboard estará disponível em `http://localhost:8501`.

## 📊 Recursos do Dashboard

### KPIs
- Total de Menções
- Percentual de Positivos
- Percentual de Negativos
- Indicador de Saúde da Marca

### Gráficos
- 📈 Evolução do sentimento médio por dia
- 🥧 Distribuição de sentimentos (pizza)
- 📱 Análise por plataforma

### Filtros
- Plataforma (Twitter, Instagram, Facebook)
- Classificação (Positivo, Negativo, Neutro)
- Período de datas

## 🧠 Tecnologias Utilizadas

| Tecnologia | Uso |
|------------|-----|
| **TextBlob** | Análise de sentimentos (NLP) |
| **Streamlit** | Dashboard interativo |
| **Plotly** | Gráficos interativos |
| **Pandas** | Manipulação de dados |
| **Faker** | Geração de dados sintéticos |

## 📈 Interpretação dos Resultados

### Polaridade
- **+1**: Muito positivo
- **0**: Neutro
- **-1**: Muito negativo

### Classificação
- **Positivo**: Polaridade > 0.1
- **Neutro**: -0.1 ≤ Polaridade ≤ 0.1
- **Negativo**: Polaridade < -0.1

## 🔮 Próximos Passos

- [ ] Integração com APIs reais (Twitter/X, Instagram)
- [ ] Análise de tópicos (Topic Modeling)
- [ ] Detecção de influenciadores
- [ ] Alertas em tempo real
- [ ] Análise de concorrentes

---

**Desenvolvido para o Hub de Criação** 🚀
