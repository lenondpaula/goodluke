"""
Visual-On-Demand — Motor de Match Visual
Algoritmo de recomendação de fotógrafos baseado em estilo visual
Simula extração de características de imagem para MVP leve
"""

import io
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

# Diretório base
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Mapeamento de estilos para vetores de características (embeddings simulados)
# Cada estilo tem um "vetor de assinatura" que representa suas características visuais
ESTILO_EMBEDDINGS = {
    "Dark_Moody": np.array([0.1, 0.2, 0.15, 0.8, 0.9, 0.7, 0.3, 0.1]),
    "Bright_Airy": np.array([0.9, 0.85, 0.95, 0.2, 0.1, 0.3, 0.8, 0.9]),
    "Black_White": np.array([0.5, 0.5, 0.5, 0.6, 0.7, 0.4, 0.1, 0.1]),
    "Vibrant_Colors": np.array([0.7, 0.3, 0.9, 0.4, 0.5, 0.8, 0.95, 0.7]),
}

# Características visuais que o algoritmo "detecta"
CARACTERISTICAS = [
    "Luminosidade", "Temperatura", "Saturacao", "Contraste",
    "Sombras", "Textura", "Vivacidade", "Suavidade"
]


def carregar_fotografos() -> pd.DataFrame:
    """Carrega a base de dados de fotógrafos."""
    path = DATA_DIR / "fotografos.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Base de fotógrafos não encontrada em {path}. "
            "Execute 'python src/gerar_talentos.py' primeiro."
        )
    return pd.read_csv(path)


def analisar_imagem_real(image: Image.Image) -> Tuple[dict, str]:
    """
    Analisa características reais da imagem usando PIL.
    
    Args:
        image: Objeto PIL Image
        
    Returns:
        Tuple com (características extraídas, estilo inferido)
    """
    # Converter para RGB se necessário
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Redimensionar para análise rápida
    image_small = image.resize((100, 100))
    pixels = np.array(image_small)
    
    # Calcular estatísticas de cor
    r, g, b = pixels[:, :, 0], pixels[:, :, 1], pixels[:, :, 2]
    
    # Luminosidade média (0-1)
    luminosidade = np.mean(pixels) / 255.0
    
    # Saturação (diferença entre canais)
    hsv_approx = np.std([np.mean(r), np.mean(g), np.mean(b)]) / 128.0
    saturacao = min(hsv_approx * 2, 1.0)
    
    # Contraste (desvio padrão geral)
    contraste = np.std(pixels) / 128.0
    contraste = min(contraste, 1.0)
    
    # Temperatura (mais vermelho = quente, mais azul = frio)
    temp_raw = (np.mean(r) - np.mean(b)) / 255.0
    temperatura = (temp_raw + 1) / 2  # Normalizar para 0-1
    
    # Verificar se é aproximadamente P&B
    is_bw = saturacao < 0.15
    
    # Determinar estilo baseado nas características
    if is_bw:
        estilo = "Black_White"
    elif luminosidade > 0.65 and saturacao < 0.4:
        estilo = "Bright_Airy"
    elif luminosidade < 0.4 and contraste > 0.3:
        estilo = "Dark_Moody"
    elif saturacao > 0.35:
        estilo = "Vibrant_Colors"
    else:
        # Fallback baseado em luminosidade
        estilo = "Bright_Airy" if luminosidade > 0.5 else "Dark_Moody"
    
    caracteristicas = {
        "Luminosidade": round(luminosidade, 2),
        "Temperatura": round(temperatura, 2),
        "Saturacao": round(saturacao, 2),
        "Contraste": round(contraste, 2),
        "Sombras": round(1 - luminosidade, 2),
        "Textura": round(contraste * 0.8, 2),
        "Vivacidade": round(saturacao * 0.9, 2),
        "Suavidade": round(1 - contraste, 2),
    }
    
    return caracteristicas, estilo


def analisar_estilo_imagem(
    uploaded_file, 
    modo: str = "auto"
) -> Tuple[str, dict, float]:
    """
    Analisa o estilo visual de uma imagem.
    
    Para o MVP, combina:
    1. Análise real de pixels (luminosidade, saturação)
    2. Detecção por nome do arquivo (se contiver keywords)
    
    Args:
        uploaded_file: Arquivo de imagem do Streamlit
        modo: "auto", "real" ou "simulado"
        
    Returns:
        Tuple com (estilo detectado, características, confiança)
    """
    # Tentar detectar pelo nome do arquivo primeiro
    filename = uploaded_file.name.lower() if hasattr(uploaded_file, "name") else ""
    
    estilo_por_nome = None
    for estilo, embedding in ESTILO_EMBEDDINGS.items():
        keywords = estilo.lower().replace("_", " ").split()
        if any(kw in filename for kw in keywords):
            estilo_por_nome = estilo
            break
    
    # Carregar e analisar a imagem
    try:
        image = Image.open(uploaded_file)
        caracteristicas, estilo_por_analise = analisar_imagem_real(image)
        
        # Se encontrou pelo nome, usa ele com alta confiança
        if estilo_por_nome:
            estilo_final = estilo_por_nome
            confianca = 0.95
        else:
            estilo_final = estilo_por_analise
            confianca = 0.75 + random.uniform(0, 0.15)
            
    except Exception:
        # Fallback para análise simulada
        estilo_final = estilo_por_nome or random.choice(list(ESTILO_EMBEDDINGS.keys()))
        caracteristicas = {k: round(random.uniform(0.3, 0.8), 2) for k in CARACTERISTICAS}
        confianca = 0.70
    
    return estilo_final, caracteristicas, round(confianca, 2)


def calcular_match_score(
    estilo_usuario: str, 
    estilo_fotografo: str,
    avaliacao: float
) -> float:
    """
    Calcula o score de compatibilidade entre usuário e fotógrafo.
    
    Args:
        estilo_usuario: Estilo detectado na imagem do usuário
        estilo_fotografo: Estilo dominante do fotógrafo
        avaliacao: Avaliação do fotógrafo (4.0 a 5.0)
        
    Returns:
        Score de match (0 a 100)
    """
    # Similaridade de cosseno entre embeddings
    emb_usuario = ESTILO_EMBEDDINGS.get(estilo_usuario, np.zeros(8))
    emb_fotografo = ESTILO_EMBEDDINGS.get(estilo_fotografo, np.zeros(8))
    
    similaridade = cosine_similarity(
        emb_usuario.reshape(1, -1),
        emb_fotografo.reshape(1, -1)
    )[0][0]
    
    # Bônus por match exato de estilo
    bonus_estilo = 15 if estilo_usuario == estilo_fotografo else 0
    
    # Bônus por avaliação alta
    bonus_avaliacao = (avaliacao - 4.0) * 5  # Até 5 pontos
    
    # Score final
    score_base = similaridade * 80  # Até 80 pontos
    score_final = score_base + bonus_estilo + bonus_avaliacao
    
    # Adicionar pequena variação para parecer mais "real"
    variacao = random.uniform(-2, 2)
    score_final = max(60, min(100, score_final + variacao))
    
    return round(score_final, 1)


def aplicar_precificacao_dinamica(
    preco_base: float,
    data_evento: Optional[datetime] = None,
    urgencia: bool = False
) -> Tuple[float, list]:
    """
    Aplica precificação dinâmica baseada em fatores de mercado.
    
    Args:
        preco_base: Preço base por hora
        data_evento: Data do evento (se fornecida)
        urgencia: Se é um pedido urgente
        
    Returns:
        Tuple com (preço ajustado, lista de ajustes aplicados)
    """
    preco = preco_base
    ajustes = []
    
    if data_evento:
        # Sábado ou Domingo: +20%
        if data_evento.weekday() >= 5:
            multiplicador = 1.20
            preco *= multiplicador
            ajustes.append(("Fim de semana", "+20%"))
        
        # Dezembro (alta temporada): +15%
        if data_evento.month == 12:
            preco *= 1.15
            ajustes.append(("Alta temporada", "+15%"))
        
        # Janeiro/Fevereiro (baixa): -10%
        if data_evento.month in [1, 2]:
            preco *= 0.90
            ajustes.append(("Baixa temporada", "-10%"))
    
    # Urgência (menos de 7 dias): +25%
    if urgencia:
        preco *= 1.25
        ajustes.append(("Urgência", "+25%"))
    
    return round(preco, 2), ajustes


def encontrar_fotografos(
    estilo_desejado: str,
    orcamento_max: Optional[float] = None,
    data_evento: Optional[datetime] = None,
    especialidade: Optional[str] = None,
    cidade: Optional[str] = None,
    top_n: int = 5
) -> pd.DataFrame:
    """
    Encontra os melhores fotógrafos para o estilo desejado.
    
    Args:
        estilo_desejado: Estilo visual detectado
        orcamento_max: Orçamento máximo por hora (opcional)
        data_evento: Data do evento (para precificação dinâmica)
        especialidade: Filtro por especialidade (opcional)
        cidade: Filtro por cidade (opcional)
        top_n: Número de resultados
        
    Returns:
        DataFrame com os fotógrafos recomendados
    """
    df = carregar_fotografos()
    
    # Filtrar apenas disponíveis
    df = df[df["Disponivel"] == True].copy()
    
    # Calcular match score para cada fotógrafo
    df["Match_Score"] = df.apply(
        lambda row: calcular_match_score(
            estilo_desejado, 
            row["Estilo_Dominante"],
            row["Avaliacao"]
        ),
        axis=1
    )
    
    # Aplicar precificação dinâmica
    urgencia = False
    if data_evento:
        dias_ate_evento = (data_evento - datetime.now()).days
        urgencia = dias_ate_evento < 7
    
    precos_dinamicos = []
    ajustes_lista = []
    
    for _, row in df.iterrows():
        preco_din, ajustes = aplicar_precificacao_dinamica(
            row["Preco_Hora"], data_evento, urgencia
        )
        precos_dinamicos.append(preco_din)
        ajustes_lista.append(ajustes)
    
    df["Preco_Dinamico"] = precos_dinamicos
    df["Ajustes_Preco"] = ajustes_lista
    
    # Filtros opcionais
    if orcamento_max:
        df = df[df["Preco_Dinamico"] <= orcamento_max]
    
    if especialidade:
        df = df[df["Especialidade"].str.contains(especialidade, case=False, na=False)]
    
    if cidade:
        df = df[df["Cidade"].str.contains(cidade, case=False, na=False)]
    
    # Ordenar por match score (descendente)
    df = df.sort_values("Match_Score", ascending=False)
    
    # Retornar top N
    return df.head(top_n).reset_index(drop=True)


def obter_insights_estilo(estilo: str) -> dict:
    """
    Retorna insights sobre um estilo visual específico.
    """
    insights = {
        "Dark_Moody": {
            "emoji": "🌑",
            "titulo": "Dark & Moody",
            "descricao": "Você busca um visual cinematográfico com tons profundos e dramáticos.",
            "ideal_para": ["Casamentos intimistas", "Ensaios artísticos", "Moda editorial"],
            "dica": "Esse estilo funciona melhor em ambientes com luz controlada ou dourada."
        },
        "Bright_Airy": {
            "emoji": "☀️",
            "titulo": "Bright & Airy",
            "descricao": "Você prefere fotos leves, luminosas e com sensação de felicidade.",
            "ideal_para": ["Casamentos ao ar livre", "Ensaios família", "Lifestyle"],
            "dica": "Agende o ensaio para a 'golden hour' (1h antes do pôr do sol)."
        },
        "Black_White": {
            "emoji": "⚫",
            "titulo": "Preto & Branco Clássico",
            "descricao": "Você valoriza a atemporalidade e o foco nas emoções e texturas.",
            "ideal_para": ["Retratos artísticos", "Documentários", "Arquitetura"],
            "dica": "O P&B destaca expressões faciais e elimina distrações de cor."
        },
        "Vibrant_Colors": {
            "emoji": "🌈",
            "titulo": "Cores Vibrantes",
            "descricao": "Você quer energia, alegria e cores que saltam aos olhos!",
            "ideal_para": ["Festas", "Eventos corporativos", "Moda street"],
            "dica": "Use roupas em cores sólidas para criar contraste interessante."
        }
    }
    return insights.get(estilo, insights["Bright_Airy"])


# Testes do motor
if __name__ == "__main__":
    print("🎨 Visual-On-Demand — Teste do Motor de Match")
    print("=" * 50)
    
    # Testar busca de fotógrafos
    print("\n🔍 Buscando fotógrafos estilo 'Dark_Moody'...")
    
    from datetime import datetime, timedelta
    
    # Simular evento no sábado
    proximo_sabado = datetime.now() + timedelta(days=(5 - datetime.now().weekday()) % 7)
    
    resultados = encontrar_fotografos(
        estilo_desejado="Dark_Moody",
        orcamento_max=400,
        data_evento=proximo_sabado,
        top_n=3
    )
    
    print(f"\n📸 Top 3 Fotógrafos Encontrados:\n")
    for i, row in resultados.iterrows():
        print(f"{i+1}. {row['Nome']}")
        print(f"   Match: {row['Match_Score']}% | R$ {row['Preco_Dinamico']}/h")
        print(f"   Estilo: {row['Estilo_Dominante']} | ⭐ {row['Avaliacao']}")
        print()
