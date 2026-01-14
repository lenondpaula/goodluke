# 🎸 GIG-Master AI

**Planejamento Inteligente de Turnês Musicais**

Sistema de otimização de turnês que combina análise preditiva com planos de marketing automatizados para maximizar lucro e minimizar custos logísticos.

---

## 🎯 Funcionalidades

### 1. Análise de Mercado
- 50 cidades brasileiras analisadas
- Métricas por cidade:
  - População e afinidade musical
  - Preço médio de ingressos
  - Capacidade de venues
  - Custo de produção estimado
  - Distância da capital de referência

### 2. Otimização de Rota
- **Algoritmo Greedy** para seleção de cidades
- **Score de Viabilidade**: `(População × Afinidade) / Distância`
- Fatores considerados:
  - Sazonalidade por mês
  - Períodos de chuva por região
  - Proximidade geográfica entre cidades
  - ROI estimado

### 3. Dashboard Interativo
- **Timeline**: Cronograma anual com Gantt chart
- **Análise de Lucro**: Comparação entre cidades
- **Mapa**: Visualização da rota no Brasil
- **Marketing**: Planos automatizados por cidade

### 4. Planos de Marketing
6 fases automatizadas por show:
1. **Aquecimento** (12 semanas antes) - Teasers e influenciadores
2. **Pré-Venda** (8 semanas antes) - Lote 1 exclusivo
3. **Venda Geral** (6 semanas antes) - Anúncios em massa
4. **Engajamento** (4 semanas antes) - Bastidores e lives
5. **Última Chamada** (1 semana antes) - Remarketing
6. **Pós-Show** (1 semana depois) - Agradecimentos e leads

---

## 📊 Resultados (Turnê Simulada)

- **12 shows** programados (1 por mês)
- **R$ 16.8M** de lucro total estimado
- **11.370 km** de distância total
- **ROI médio**: 2839%

### Top 5 Cidades por Lucro Potencial:
1. São Paulo/SP - R$ 5.5M
2. Rio de Janeiro/RJ - R$ 1.7M
3. Diadema/SP - R$ 1.3M
4. Curitiba/PR - R$ 1.1M
5. Osasco/SP - R$ 1.2M

---

## 🚀 Como Usar

### 1. Gerar Dados de Mercado
```bash
cd projeto-gig-master
python src/gerar_mercado.py
```

Gera arquivo `data/mercado_shows.csv` com:
- 50 cidades brasileiras
- Métricas de mercado simuladas
- Dados geográficos (latitude/longitude)

### 2. Otimizar Rota da Turnê
```bash
python src/motor_logistica.py
```

Gera dois arquivos:
- `data/plano_turne.csv` - Cronograma de 12 shows
- `data/planos_marketing.json` - Planos detalhados por cidade

### 3. Executar Dashboard
```bash
streamlit run pages/6_GIG_Master_AI.py
```

Ou via homepage do hub:
```bash
streamlit run streamlit_app.py
```

---

## 📁 Estrutura do Projeto

```
projeto-gig-master/
├── requirements.txt          # Dependências
├── app/
│   └── gig_dashboard.py      # Dashboard principal
├── data/
│   ├── mercado_shows.csv     # Dados de mercado
│   ├── plano_turne.csv       # Cronograma otimizado
│   └── planos_marketing.json # Planos de marketing
└── src/
    ├── gerar_mercado.py      # Gerador de dados
    └── motor_logistica.py    # Motor de otimização
```

---

## 🛠️ Tecnologias

- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações (Gantt, mapas, gráficos)
- **Faker**: Geração de dados sintéticos
- **Scikit-learn**: Algoritmos de otimização

---

## 📈 Métricas do Dashboard

### KPIs Principais
- Shows planejados
- Lucro total estimado
- Distância total percorrida
- ROI médio

### Análises Disponíveis
- Timeline anual com cores por região
- Comparação de lucro entre cidades
- Mapa interativo da rota
- Distribuição de lucro por região (pizza)
- Top 5 cidades por ROI

### Exportações
- **HTML**: Relatório completo do plano anual
- **CSV**: Cronograma detalhado

---

## 🎨 Design

- **Tema adaptável**: Funciona em tema claro e escuro
- **CSS corporativo**: Consistente com outros apps do hub
- **Cores por região**:
  - 🔵 Sudeste
  - 🟢 Sul
  - 🟠 Nordeste
  - 🟣 Norte
  - 🔴 Centro-Oeste

---

## 🌐 Deploy no Streamlit Cloud

O app está pronto para deploy:

✅ Dados pré-gerados inclusos no repositório  
✅ Tema adaptável (claro/escuro)  
✅ Dependências em `requirements.txt` na raiz  
✅ CSS com bom contraste em qualquer tema  
✅ Geração automática de dados se necessário  

---

## 📝 Observações

- **Dados Sintéticos**: Todos os dados são simulados para demonstração
- **Algoritmo Simples**: Usa heurística greedy (não garante solução ótima global)
- **Sazonalidade**: Considera períodos de chuva e demanda por região
- **Distância**: Usa fórmula de Haversine para cálculo de km

---

## 🎯 Casos de Uso

1. **Bandas/Artistas**: Planejar turnês maximizando lucro
2. **Produtoras**: Avaliar viabilidade de shows por região
3. **Marketing**: Cronograma automatizado de campanhas
4. **Logística**: Otimização de rotas e custos

---

## 🔮 Melhorias Futuras

- [ ] Integração com APIs reais (Spotify, Ticketmaster)
- [ ] Algoritmos mais sofisticados (TSP, Genetic Algorithm)
- [ ] Consideração de múltiplos shows na mesma cidade
- [ ] Análise de concorrência (outros artistas)
- [ ] Integração com calendário de feriados regionais
- [ ] Análise de risco (cancelamentos, clima)

---

**Desenvolvido por Lenon de Paula**  
Portfolio: [goodluke](https://github.com/lenondpaula/goodluke)
