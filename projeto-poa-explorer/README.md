# 🗺️ PoA-Insight Explorer

**Sistema de Turismo Inteligente para Porto Alegre**

Plataforma que transforma o turismo tradicional em **Smart Tourism**, oferecendo recomendações contextuais baseadas em clima, horário e preferências do usuário.

---

## 🎯 Funcionalidades

### 1. Recomendação Contextual
O motor de turismo considera três dimensões para personalizar sugestões:

| Dimensão | Impacto |
|----------|---------|
| **Clima** | Com chuva → apenas locais cobertos (Indoor) |
| **Horário** | Manhã/Tarde/Noite → prioriza atividades adequadas |
| **Perfil** | Natureza/Cultura/Gastronomia/Festa → filtra categorias |

### 2. Base Georreferenciada
- **30 pontos turísticos reais** de Porto Alegre
- Coordenadas precisas (Lat/Lon)
- 5 categorias: Parque, Museu, Gastronomia, Vida Noturna, Cultura
- Classificação Indoor/Outdoor
- Horário de pico de cada local

### 3. Mapa Interativo (Folium)
- Marcadores coloridos por categoria
- Popups com informações detalhadas
- Zoom e navegação fluida
- Estilo CartoDB positron (limpo)

### 4. Mapa de Calor Dinâmico
Simula a concentração de pessoas em diferentes horários:

| Horário | Zonas de Calor |
|---------|----------------|
| **Manhã** | Centro Histórico, Mercado Público |
| **Tarde** | Orla do Guaíba, Redenção, Parcão |
| **Noite** | Cidade Baixa, Padre Chagas |

---

## 📍 Locais Incluídos

### Parques (Outdoor)
- Parque da Redenção (Farroupilha)
- Orla do Guaíba (Gasômetro)
- Parque Moinhos de Vento (Parcão)
- Parque Marinha do Brasil
- Jardim Botânico

### Museus (Indoor)
- Fundação Iberê Camargo
- MARGS - Museu de Arte do RS
- Museu de Ciências e Tecnologia (PUCRS)
- Memorial do RS
- Museu Júlio de Castilhos

### Gastronomia
- Mercado Público
- Rua Padre Chagas
- Gambrinus
- Chalé da Praça XV
- Banca 40

### Vida Noturna
- Cidade Baixa (Polo)
- Ocidente Bar
- Opinião (Casa de Shows)
- Beco do Espelho
- Agulha Bar

### Cultura
- Casa de Cultura Mario Quintana
- Theatro São Pedro
- Santander Cultural
- Usina do Gasômetro
- Cinemateca Capitólio

---

## 🚀 Como Usar

### 1. Gerar Base de Locais
```bash
cd projeto-poa-explorer
python src/gerar_locais_poa.py
```

**O que é gerado:**
- `data/locais_poa.csv` — 30 pontos turísticos com coordenadas

### 2. Testar Motor de Recomendação
```bash
python src/motor_turismo.py
```

**Cenários testados:**
- Natureza + Sol + Tarde → Parques
- Natureza + Chuva + Tarde → Nenhum (locais outdoor eliminados)
- Festa + Sol + Noite → Vida Noturna
- Cultura + Chuva + Manhã → Museus

### 3. Executar Dashboard
```bash
# Via página específica
streamlit run pages/8_PoA_Insight_Explorer.py

# Ou via homepage do hub
streamlit run streamlit_app.py
```

---

## 📁 Estrutura do Projeto

```
projeto-poa-explorer/
├── requirements.txt          # Dependências (Folium, Streamlit-Folium)
├── app/
│   └── poa_dashboard.py      # Dashboard com mapa interativo
├── data/
│   └── locais_poa.csv        # Base de 30 POIs de Porto Alegre
└── src/
    ├── gerar_locais_poa.py   # Gerador da base georreferenciada
    └── motor_turismo.py      # Motor de recomendação contextual
```

---

## 🔬 Lógica do Motor de Recomendação

### Filtro de Clima
```python
if clima == "Chuva":
    df = df[df["Tipo"] == "Indoor"]  # Remove todos os Outdoor
```

### Boost de Horário
```python
HORARIO_BOOST = {
    "Manhã": {"Parque": 1.3, "Vida Noturna": 0.3, ...},
    "Tarde": {"Parque": 1.2, "Museu": 1.3, ...},
    "Noite": {"Parque": 0.4, "Vida Noturna": 1.5, ...},
}
```

### Filtro de Perfil
```python
PERFIL_CATEGORIAS = {
    "Natureza": ["Parque"],
    "Cultura": ["Museu", "Cultura"],
    "Gastronomia": ["Gastronomia"],
    "Festa": ["Vida Noturna", "Gastronomia"],
    "Explorador": ["Parque", "Museu", "Cultura", "Gastronomia"],
}
```

### Score Final
```python
score = popularidade_base * boost_horario * (1.2 se horario_pico == horario else 1.0)
```

---

## 🎨 Interface do Dashboard

### Sidebar (Controles)
- **Perfil:** Explorador, Natureza, Cultura, Gastronomia, Festa
- **Clima:** Sol ou Chuva
- **Horário:** Manhã, Tarde ou Noite
- **Opções:** Mostrar Heatmap, Mostrar Todos os Locais

### Área Principal
- **Mapa:** Folium com marcadores coloridos e heatmap
- **Lista:** Cards com os 5 locais recomendados
- **Estatísticas:** Contagem por tipo e categoria

### Cores dos Marcadores
- 🟢 Verde → Parques
- 🔵 Azul → Museus
- 🟠 Laranja → Gastronomia
- 🩷 Rosa → Vida Noturna
- 🟣 Roxo → Cultura

---

## 💡 Casos de Uso

### 1. Turista em Dia Chuvoso
- **Contexto:** Chuva, Tarde, Perfil Cultura
- **Resultado:** Museus e centros culturais cobertos
- **Sugestões:** Iberê Camargo, MARGS, Casa de Cultura Mario Quintana

### 2. Noite de Sexta-Feira
- **Contexto:** Sol, Noite, Perfil Festa
- **Resultado:** Vida noturna e gastronomia
- **Sugestões:** Cidade Baixa, Padre Chagas, Ocidente Bar

### 3. Domingo de Sol
- **Contexto:** Sol, Tarde, Perfil Natureza
- **Resultado:** Parques e áreas verdes
- **Sugestões:** Redenção (Brique!), Orla do Guaíba, Parcão

### 4. Família com Crianças
- **Contexto:** Sol, Manhã, Perfil Explorador
- **Resultado:** Atividades variadas para família
- **Sugestões:** Museu de Ciências PUCRS, Jardim Botânico

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **Streamlit** — Interface web interativa
- **Folium** — Mapas interativos baseados em Leaflet
- **Streamlit-Folium** — Integração Folium ↔ Streamlit
- **Branca** — Legendas e colormap para mapas
- **GeoPy** — Cálculo de distâncias geodésicas
- **Pandas/NumPy** — Manipulação de dados

---

## 🌟 Diferenciais

1. **Contextualização Real**
   - Parque é ótimo com sol, péssimo com chuva
   - Bar é vazio às 18h, lotado às 22h
   - O sistema entende essas nuances

2. **Dados Reais de POA**
   - 30 locais reais com coordenadas precisas
   - Categorização baseada em conhecimento local
   - Preços e horários de pico realistas

3. **Visualização Imersiva**
   - Mapa de calor mostra "onde está a galera"
   - Marcadores coloridos facilitam identificação
   - Popups com informações completas

---

## 📈 Próximos Passos (Roadmap)

- [ ] Integração com API de clima real (OpenWeatherMap)
- [ ] Rotas otimizadas entre pontos (Google Maps API)
- [ ] Avaliações de usuários em tempo real
- [ ] Eventos temporários (shows, festivais)
- [ ] Versão mobile com geolocalização

---

## 👨‍💻 Autor

**Lenon de Paula**  
Especialista em Ciência de Dados e IA  
[lenondpaula@gmail.com](mailto:lenondpaula@gmail.com)

---

## 📄 Licença

Este projeto faz parte do portfólio de demonstração. Uso livre para fins educacionais.
