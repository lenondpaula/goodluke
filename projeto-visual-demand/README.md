# 📸 Visual-On-Demand — Marketplace Visual de Fotógrafos

> **"O Shazam para encontrar o fotógrafo perfeito"**

Sistema de matching visual inteligente que conecta clientes a fotógrafos baseado em análise de estilo visual. Em vez de filtrar por texto, o cliente faz upload de uma foto que amou e o algoritmo encontra fotógrafos com assinatura visual similar.

![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red?logo=streamlit)
![PIL](https://img.shields.io/badge/Pillow-10.0+-green)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange)

---

## 🎯 O Problema

A indústria criativa sofre com a subjetividade: o que é uma foto "bonita" para um cliente é "escura" para outro. Descrições textuais como "fotógrafo de casamento" não capturam a essência do estilo visual desejado.

## 💡 A Solução

Visual-On-Demand usa **Visão Computacional** para analisar a "assinatura visual" de uma imagem de referência e encontrar fotógrafos cujo portfólio tenha estilo similar.

---

## 🚀 Quick Start

```bash
# 1. Gerar base de fotógrafos (50 perfis sintéticos)
cd projeto-visual-demand
python src/gerar_talentos.py

# 2. Rodar o dashboard
streamlit run app/visual_market.py

# Ou via Hub principal
cd .. && streamlit run streamlit_app.py
# → Acessar "App 9 — Visual-On-Demand"
```

---

## 📁 Estrutura do Projeto

```
projeto-visual-demand/
├── app/
│   ├── __init__.py
│   └── visual_market.py      # Dashboard Streamlit (interface)
├── assets/
│   └── portfolio/            # Imagens de exemplo para testes
├── data/
│   ├── fotografos.csv        # Base de 50 fotógrafos
│   └── estilos_referencia.csv # Tabela de estilos
├── src/
│   ├── __init__.py
│   ├── gerar_talentos.py     # Gerador de dados sintéticos
│   └── motor_match.py        # Motor de matching visual
├── requirements.txt
└── README.md
```

---

## 🎨 Estilos Visuais Reconhecidos

| Estilo | Emoji | Características | Ideal Para |
|--------|-------|-----------------|------------|
| **Dark & Moody** | 🌑 | Tons escuros, sombras dramáticas, cinematográfico | Casamentos intimistas, moda editorial |
| **Bright & Airy** | ☀️ | Luminoso, tons pastéis, leve e feliz | Casamentos ao ar livre, lifestyle |
| **Black & White** | ⚫ | Clássico, atemporal, foco em emoções | Retratos artísticos, documentários |
| **Vibrant Colors** | 🌈 | Cores saturadas, energético | Festas, eventos corporativos |

---

## 🧠 Como Funciona

### 1. Análise de Imagem (PIL)

O motor extrai características reais da imagem usando processamento de pixels:

```python
# Características extraídas
- Luminosidade:  média de pixels (0-1)
- Saturação:     diferença entre canais RGB
- Contraste:     desvio padrão geral
- Temperatura:   vermelho vs azul (quente/frio)
```

### 2. Classificação de Estilo

Regras baseadas nas características:

| Condição | Estilo Classificado |
|----------|---------------------|
| Saturação < 15% | Black & White |
| Luminosidade > 65% e Saturação < 40% | Bright & Airy |
| Luminosidade < 40% e Contraste > 30% | Dark & Moody |
| Saturação > 35% | Vibrant Colors |

### 3. Match Score

Calcula compatibilidade usando:

1. **Similaridade de Cosseno** entre embeddings de estilo (até 80 pts)
2. **Bônus por Match Exato** de estilo (+15 pts)
3. **Bônus por Avaliação** alta do fotógrafo (até +5 pts)

### 4. Precificação Dinâmica

| Fator | Ajuste |
|-------|--------|
| Sábado/Domingo | +20% |
| Dezembro (alta temporada) | +15% |
| Janeiro/Fevereiro (baixa) | -10% |
| Urgência (<7 dias) | +25% |

---

## 📊 Base de Dados

O script `gerar_talentos.py` cria 50 fotógrafos fictícios com:

| Campo | Descrição |
|-------|-----------|
| `ID` | Identificador único (FOT-0001) |
| `Nome` | Nome gerado com Faker (pt_BR) |
| `Especialidade` | Casamentos, Moda, Produtos, etc. |
| `Estilo_Dominante` | Um dos 4 estilos visuais |
| `Equipamento` | Sony, Canon, Nikon, Fujifilm, Leica |
| `Preco_Hora` | R$ 150-500 (ajustado por avaliação) |
| `Avaliacao` | 4.0 a 5.0 estrelas |
| `Projetos_Concluidos` | 20-500 projetos |
| `Link_Portfolio` | URL fictícia |

---

## 🔮 Evolução com GPU

Em ambiente com GPU, o motor pode usar embeddings reais com CLIP:

```python
from transformers import CLIPProcessor, CLIPModel

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Extrair embeddings de 512 dimensões
inputs = processor(images=image, return_tensors="pt")
embeddings = model.get_image_features(**inputs)
```

---

## 📦 Dependências

```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
Pillow>=10.0.0
scikit-learn>=1.3.0
faker>=19.0.0
```

---

## ✅ Funcionalidades

- [x] Upload de imagem de referência (JPG, PNG, WEBP)
- [x] Análise de paleta de cores e iluminação
- [x] Matching com embeddings simulados
- [x] Precificação dinâmica por dia/temporada/urgência
- [x] Filtros: orçamento, data do evento, especialidade
- [x] Cards visuais com Match Score
- [x] Botão "Contratar Agora" com feedback
- [x] Interface moderna com CSS corporativo

---

## 🧪 Testes

```bash
# Testar motor de match
python src/motor_match.py

# Testar geração de dados
python src/gerar_talentos.py
```

---

## 📄 Licença

Parte do Hub de Criação — Portfolio de Lenon de Paula

---

*Hub de Criação — App 9: Visual-On-Demand*
