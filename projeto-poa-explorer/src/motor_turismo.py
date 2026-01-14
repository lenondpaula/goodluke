# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
PoA-Insight Explorer - Motor de Turismo Contextual
Recomendação inteligente baseada em clima, horário e preferências
"""

from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

import pandas as pd
import numpy as np

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Mapeamento de perfis para categorias preferidas
PERFIL_CATEGORIAS = {
    "Natureza": ["Parque"],
    "Cultura": ["Museu", "Cultura"],
    "Gastronomia": ["Gastronomia"],
    "Festa": ["Vida Noturna", "Gastronomia"],
    "Explorador": ["Parque", "Museu", "Cultura", "Gastronomia"],  # Gosta de tudo
}

# Mapeamento de horários para preferências
HORARIO_BOOST = {
    "Manhã": {"Parque": 1.3, "Museu": 1.1, "Gastronomia": 1.0, "Cultura": 1.0, "Vida Noturna": 0.3},
    "Tarde": {"Parque": 1.2, "Museu": 1.3, "Gastronomia": 1.1, "Cultura": 1.3, "Vida Noturna": 0.5},
    "Noite": {"Parque": 0.4, "Museu": 0.3, "Gastronomia": 1.3, "Cultura": 1.0, "Vida Noturna": 1.5},
}

# Zonas de calor por horário (simulação de concentração de pessoas)
ZONAS_CALOR = {
    "Manhã": {
        "centro": {"lat": -30.0300, "lon": -51.2280, "intensidade": 0.8},  # Centro/Mercado
        "redenção": {"lat": -30.0392, "lon": -51.2172, "intensidade": 0.6},  # Exercícios matinais
    },
    "Tarde": {
        "orla": {"lat": -30.0345, "lon": -51.2420, "intensidade": 0.9},  # Pôr do sol
        "redenção": {"lat": -30.0392, "lon": -51.2172, "intensidade": 0.8},  # Lazer
        "moinhos": {"lat": -30.0275, "lon": -51.2005, "intensidade": 0.7},  # Parcão
    },
    "Noite": {
        "cidade_baixa": {"lat": -30.0420, "lon": -51.2180, "intensidade": 1.0},  # Boemia
        "padre_chagas": {"lat": -30.0265, "lon": -51.2025, "intensidade": 0.8},  # Gastronomia
    },
}


def carregar_locais() -> pd.DataFrame:
    """Carrega base de locais de Porto Alegre."""
    csv_path = DATA_DIR / "locais_poa.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Base de locais não encontrada: {csv_path}\n"
            "Execute primeiro: python src/gerar_locais_poa.py"
        )
    
    return pd.read_csv(csv_path)


def filtrar_por_clima(df: pd.DataFrame, clima: str) -> pd.DataFrame:
    """
    Filtra locais baseado no clima atual.
    
    Se chuva: remove todos os locais Outdoor
    Se sol: mantém todos
    """
    if clima.lower() in ["chuva", "chuvoso", "rain"]:
        # Com chuva, apenas locais Indoor são viáveis
        df_filtrado = df[df["Tipo"] == "Indoor"].copy()
        return df_filtrado
    
    # Com sol, todos os locais são viáveis
    return df.copy()


def filtrar_por_horario(df: pd.DataFrame, horario: str) -> pd.DataFrame:
    """
    Ajusta scores baseado no horário do dia.
    
    - Manhã: prioriza parques e museus
    - Tarde: mantém equilíbrio
    - Noite: prioriza vida noturna e gastronomia
    """
    df_ajustado = df.copy()
    
    # Aplicar boost de horário
    boosts = HORARIO_BOOST.get(horario, HORARIO_BOOST["Tarde"])
    
    def calcular_boost(row):
        categoria = row["Categoria"]
        boost = boosts.get(categoria, 1.0)
        
        # Boost extra se o horário de pico combina
        if row["Horario_Pico"] == horario:
            boost *= 1.2
        
        return boost
    
    df_ajustado["Boost_Horario"] = df_ajustado.apply(calcular_boost, axis=1)
    df_ajustado["Score_Ajustado"] = df_ajustado["Popularidade_Base"] * df_ajustado["Boost_Horario"]
    
    return df_ajustado


def filtrar_por_perfil(df: pd.DataFrame, perfil: str) -> pd.DataFrame:
    """
    Filtra locais baseado no perfil do usuário.
    
    Perfis:
    - Natureza: prioriza parques
    - Cultura: prioriza museus e cultura
    - Gastronomia: prioriza restaurantes
    - Festa: prioriza vida noturna
    - Explorador: aceita tudo
    """
    categorias_preferidas = PERFIL_CATEGORIAS.get(perfil, PERFIL_CATEGORIAS["Explorador"])
    
    df_filtrado = df[df["Categoria"].isin(categorias_preferidas)].copy()
    
    # Se não encontrou nada, retorna todos
    if df_filtrado.empty:
        return df.copy()
    
    return df_filtrado


def recomendar_roteiro(
    perfil_usuario: str,
    clima_atual: str,
    hora_atual: str,
    top_n: int = 5,
    df_locais: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Motor principal de recomendação contextual.
    
    Pipeline:
    1. Carrega base de locais
    2. Filtra por clima (remove Outdoor se chuva)
    3. Filtra por perfil (categorias preferidas)
    4. Ajusta scores por horário
    5. Ordena por score e retorna top N
    
    Args:
        perfil_usuario: "Natureza", "Cultura", "Gastronomia", "Festa" ou "Explorador"
        clima_atual: "Sol" ou "Chuva"
        hora_atual: "Manhã", "Tarde" ou "Noite"
        top_n: Número de recomendações (default: 5)
        df_locais: DataFrame opcional (para testes)
    
    Returns:
        DataFrame com top N locais recomendados
    """
    # 1. Carregar dados
    if df_locais is None:
        df = carregar_locais()
    else:
        df = df_locais.copy()
    
    # 2. Filtrar por clima
    df = filtrar_por_clima(df, clima_atual)
    
    if df.empty:
        return pd.DataFrame()
    
    # 3. Ajustar scores por horário
    df = filtrar_por_horario(df, hora_atual)
    
    # 4. Filtrar por perfil
    df = filtrar_por_perfil(df, perfil_usuario)
    
    if df.empty:
        return pd.DataFrame()
    
    # 5. Ordenar por score e retornar top N
    df_ordenado = df.sort_values("Score_Ajustado", ascending=False).head(top_n)
    
    return df_ordenado[["ID", "Nome", "Categoria", "Lat", "Lon", "Preco_Medio", 
                         "Tipo", "Horario_Pico", "Score_Ajustado", "Descricao"]]


def gerar_zonas_calor(horario: str) -> List[Dict]:
    """
    Gera pontos de calor para HeatMap baseado no horário.
    
    Retorna lista de dicts com lat, lon e intensidade.
    """
    zonas = ZONAS_CALOR.get(horario, ZONAS_CALOR["Tarde"])
    
    pontos = []
    for nome, dados in zonas.items():
        # Gerar pontos ao redor da zona para criar efeito de calor
        for _ in range(int(dados["intensidade"] * 50)):
            lat_offset = np.random.normal(0, 0.005)
            lon_offset = np.random.normal(0, 0.005)
            pontos.append({
                "lat": dados["lat"] + lat_offset,
                "lon": dados["lon"] + lon_offset,
                "intensidade": dados["intensidade"],
            })
    
    return pontos


def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula distância aproximada em km usando fórmula de Haversine.
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Raio da Terra em km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def main():
    """Teste do motor de recomendação."""
    print("🗺️  PoA-Insight Explorer - Motor de Turismo")
    print("=" * 50)
    
    # Cenários de teste
    cenarios = [
        {"perfil": "Natureza", "clima": "Sol", "horario": "Tarde"},
        {"perfil": "Natureza", "clima": "Chuva", "horario": "Tarde"},
        {"perfil": "Festa", "clima": "Sol", "horario": "Noite"},
        {"perfil": "Cultura", "clima": "Chuva", "horario": "Manhã"},
    ]
    
    for cenario in cenarios:
        print(f"\n📍 Cenário: {cenario['perfil']} | {cenario['clima']} | {cenario['horario']}")
        print("-" * 50)
        
        recomendacoes = recomendar_roteiro(
            perfil_usuario=cenario["perfil"],
            clima_atual=cenario["clima"],
            hora_atual=cenario["horario"],
            top_n=3
        )
        
        if recomendacoes.empty:
            print("   ⚠️ Nenhuma recomendação disponível")
        else:
            for _, local in recomendacoes.iterrows():
                print(f"   ✓ {local['Nome']} ({local['Categoria']}) - Score: {local['Score_Ajustado']:.1f}")
    
    print("\n✅ Testes do motor concluídos!")


if __name__ == "__main__":
    main()
