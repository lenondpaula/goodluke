"""
GIG-Master AI - Motor de Logística e Otimização
Calcula as melhores rotas e datas para a turnê anual
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import numpy as np

# Configuração para reprodutibilidade
random.seed(42)
np.random.seed(42)

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# Meses do ano para planejamento
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

# Fatores sazonais por mês (multiplicador de demanda)
FATORES_SAZONAIS = {
    1: 0.7,   # Janeiro - férias, público disperso
    2: 0.8,   # Fevereiro - Carnaval
    3: 0.9,   # Março - volta às aulas
    4: 1.0,   # Abril - estabilização
    5: 1.1,   # Maio - Dia das Mães
    6: 1.2,   # Junho - Festas Juninas
    7: 1.3,   # Julho - férias escolares
    8: 1.1,   # Agosto - volta às aulas
    9: 1.0,   # Setembro - primavera
    10: 1.2,  # Outubro - clima agradável
    11: 1.1,  # Novembro - Black Friday
    12: 0.9,  # Dezembro - festas de fim de ano
}

# Períodos de chuva por região (meses a evitar)
MESES_CHUVA = {
    "Sudeste": [12, 1, 2, 3],
    "Sul": [6, 7, 8],  # Inverno
    "Nordeste": [4, 5, 6, 7],
    "Centro-Oeste": [11, 12, 1, 2, 3],
    "Norte": [1, 2, 3, 4, 5],
}


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância aproximada em km usando fórmula de Haversine."""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Raio da Terra em km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def calcular_score_viabilidade(row: pd.Series, mes: int = None) -> float:
    """
    Calcula o score de viabilidade de show.
    Fórmula: (População * Afinidade) / (Distância + 1) * Fator_Sazonal
    """
    populacao = row["populacao"]
    afinidade = row["afinidade_musical"]
    distancia = row["distancia_capital_km"]
    regiao = row["regiao"]
    
    # Score base
    score_base = (populacao * afinidade) / (distancia + 100)  # +100 para evitar divisão por zero
    
    # Normalizar para escala 0-100
    score_normalizado = min(100, score_base / 100000)
    
    # Aplicar fator sazonal se mês especificado
    if mes:
        fator_sazonal = FATORES_SAZONAIS.get(mes, 1.0)
        
        # Penalizar meses chuvosos para a região
        if mes in MESES_CHUVA.get(regiao, []):
            fator_sazonal *= 0.6  # Redução de 40% em meses chuvosos
        
        score_normalizado *= fator_sazonal
    
    return round(score_normalizado, 2)


def calcular_roi_estimado(row: pd.Series) -> float:
    """Calcula ROI estimado do show."""
    lucro = row["lucro_potencial"]
    custo = row["custo_producao_estimado"]
    
    if custo > 0:
        roi = (lucro / custo) * 100
    else:
        roi = 0
    
    return round(roi, 2)


def otimizar_rota_greedy(df: pd.DataFrame, n_cidades: int = 12) -> List[Dict]:
    """
    Algoritmo guloso para otimizar rota da turnê.
    Minimiza deslocamento geográfico enquanto maximiza viabilidade.
    """
    # Calcular scores para cada cidade
    df = df.copy()
    df["score_viabilidade"] = df.apply(
        lambda row: calcular_score_viabilidade(row), axis=1
    )
    df["roi_estimado"] = df.apply(calcular_roi_estimado, axis=1)
    
    # Começar pela cidade com maior score
    df_ordenado = df.sort_values("score_viabilidade", ascending=False)
    
    # Selecionar top cidades candidatas (2x o necessário para otimização)
    candidatas = df_ordenado.head(n_cidades * 2).copy()
    
    # Iniciar com a melhor cidade
    rota = []
    cidades_usadas = set()
    
    # Primeira cidade: maior score
    primeira = candidatas.iloc[0]
    rota.append({
        "mes": 1,
        "mes_nome": MESES[0],
        "cidade": primeira["cidade"],
        "estado": primeira["estado"],
        "regiao": primeira["regiao"],
        "latitude": primeira["latitude"],
        "longitude": primeira["longitude"],
        "score_viabilidade": primeira["score_viabilidade"],
        "lucro_potencial": primeira["lucro_potencial"],
        "roi_estimado": primeira["roi_estimado"],
        "preco_medio_ingresso": primeira["preco_medio_ingresso"],
        "capacidade_venue": primeira["capacidade_venue"],
        "distancia_anterior": 0,
    })
    cidades_usadas.add(primeira["cidade"])
    
    # Para cada mês seguinte, escolher cidade próxima com bom score
    for mes in range(2, n_cidades + 1):
        ultima = rota[-1]
        lat_atual = ultima["latitude"]
        lon_atual = ultima["longitude"]
        
        melhor_score = -1
        melhor_cidade = None
        melhor_distancia = 0
        
        for _, row in candidatas.iterrows():
            if row["cidade"] in cidades_usadas:
                continue
            
            # Calcular distância da cidade atual
            distancia = calcular_distancia(
                lat_atual, lon_atual,
                row["latitude"], row["longitude"]
            )
            
            # Score combinado: viabilidade ajustada pelo mês - penalidade por distância
            score_mes = calcular_score_viabilidade(row, mes)
            
            # Penalidade por distância (quanto mais longe, menor o score)
            penalidade_distancia = distancia / 1000  # Normalizar
            score_combinado = score_mes - penalidade_distancia
            
            # Bônus se a região é ideal para o mês
            if mes not in MESES_CHUVA.get(row["regiao"], []):
                score_combinado *= 1.2
            
            if score_combinado > melhor_score:
                melhor_score = score_combinado
                melhor_cidade = row
                melhor_distancia = distancia
        
        if melhor_cidade is not None:
            rota.append({
                "mes": mes,
                "mes_nome": MESES[mes - 1],
                "cidade": melhor_cidade["cidade"],
                "estado": melhor_cidade["estado"],
                "regiao": melhor_cidade["regiao"],
                "latitude": melhor_cidade["latitude"],
                "longitude": melhor_cidade["longitude"],
                "score_viabilidade": calcular_score_viabilidade(melhor_cidade, mes),
                "lucro_potencial": melhor_cidade["lucro_potencial"],
                "roi_estimado": melhor_cidade["roi_estimado"],
                "preco_medio_ingresso": melhor_cidade["preco_medio_ingresso"],
                "capacidade_venue": melhor_cidade["capacidade_venue"],
                "distancia_anterior": round(melhor_distancia, 1),
            })
            cidades_usadas.add(melhor_cidade["cidade"])
    
    return rota


def gerar_plano_marketing(cidade: str, mes: int, mes_nome: str) -> Dict:
    """
    Gera plano de marketing macro para cada cidade/mês.
    Segue cronograma típico de lançamento de shows.
    """
    # Calcular datas relativas ao show (assumindo show no dia 15 do mês)
    ano_atual = datetime.now().year + 1  # Planejamento para próximo ano
    data_show = datetime(ano_atual, mes, 15)
    
    # Fases do marketing
    fases = [
        {
            "fase": "Aquecimento",
            "semanas_antes": 12,
            "atividades": [
                "Teasers misteriosos nas redes sociais",
                "Anúncio da cidade no perfil oficial",
                "Parcerias com influenciadores locais",
            ],
            "canais": ["Instagram", "TikTok", "Twitter/X"],
            "investimento_sugerido": "15%",
        },
        {
            "fase": "Pré-Venda",
            "semanas_antes": 8,
            "atividades": [
                "Abertura de pré-venda para fã-clube",
                "Lote 1 com desconto especial",
                "Email marketing para base de leads",
            ],
            "canais": ["Email", "WhatsApp", "Site Oficial"],
            "investimento_sugerido": "20%",
        },
        {
            "fase": "Venda Geral",
            "semanas_antes": 6,
            "atividades": [
                "Lançamento do Lote 2",
                "Anúncios pagos em massa",
                "Parcerias com rádios locais",
            ],
            "canais": ["Facebook Ads", "Google Ads", "Rádio"],
            "investimento_sugerido": "35%",
        },
        {
            "fase": "Engajamento",
            "semanas_antes": 4,
            "atividades": [
                "Conteúdo de bastidores",
                "Lives com o artista",
                "Contagem regressiva",
            ],
            "canais": ["Instagram Stories", "YouTube", "TikTok"],
            "investimento_sugerido": "15%",
        },
        {
            "fase": "Última Chamada",
            "semanas_antes": 1,
            "atividades": [
                "Últimos ingressos disponíveis",
                "Remarketing intensivo",
                "Cobertura de imprensa local",
            ],
            "canais": ["Todos os canais", "Imprensa", "OOH Local"],
            "investimento_sugerido": "10%",
        },
        {
            "fase": "Pós-Show",
            "semanas_antes": -1,
            "atividades": [
                "Publicação de fotos e vídeos",
                "Agradecimento aos fãs",
                "Captação de leads para próximas datas",
            ],
            "canais": ["Instagram", "YouTube", "Email"],
            "investimento_sugerido": "5%",
        },
    ]
    
    # Calcular datas específicas para cada fase
    cronograma = []
    for fase in fases:
        semanas = fase["semanas_antes"]
        if semanas >= 0:
            data_fase = data_show - timedelta(weeks=semanas)
        else:
            data_fase = data_show + timedelta(weeks=abs(semanas))
        
        cronograma.append({
            **fase,
            "data_inicio": data_fase.strftime("%d/%m/%Y"),
        })
    
    return {
        "cidade": cidade,
        "mes": mes,
        "mes_nome": mes_nome,
        "data_show": data_show.strftime("%d/%m/%Y"),
        "cronograma": cronograma,
    }


def gerar_plano_anual(rota: List[Dict]) -> pd.DataFrame:
    """Gera DataFrame com o plano anual completo."""
    dados = []
    
    distancia_total = 0
    lucro_acumulado = 0
    
    for show in rota:
        distancia_total += show["distancia_anterior"]
        lucro_acumulado += show["lucro_potencial"]
        
        dados.append({
            "Mês": show["mes_nome"],
            "Cidade": f"{show['cidade']}/{show['estado']}",
            "Região": show["regiao"],
            "Score": show["score_viabilidade"],
            "Lucro Potencial (R$)": show["lucro_potencial"],
            "ROI (%)": show["roi_estimado"],
            "Preço Ingresso (R$)": show["preco_medio_ingresso"],
            "Capacidade Venue": show["capacidade_venue"],
            "Distância do Anterior (km)": show["distancia_anterior"],
            "Distância Acumulada (km)": round(distancia_total, 1),
            "Lucro Acumulado (R$)": round(lucro_acumulado, 2),
        })
    
    return pd.DataFrame(dados)


def carregar_mercado() -> pd.DataFrame:
    """Carrega dados de mercado de shows."""
    csv_path = DATA_DIR / "mercado_shows.csv"
    
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Arquivo de mercado não encontrado: {csv_path}\n"
            "Execute primeiro: python src/gerar_mercado.py"
        )
    
    return pd.read_csv(csv_path)


def main():
    """Função principal - gera plano de turnê otimizado."""
    print("🎸 GIG-Master AI - Motor de Logística")
    print("=" * 50)
    
    # Carregar dados de mercado
    print("\n📂 Carregando dados de mercado...")
    try:
        df_mercado = carregar_mercado()
        print(f"✅ {len(df_mercado)} cidades carregadas")
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return
    
    # Otimizar rota
    print("\n🗺️ Otimizando rota da turnê...")
    rota = otimizar_rota_greedy(df_mercado, n_cidades=12)
    print(f"✅ Rota com {len(rota)} cidades definida")
    
    # Gerar plano anual
    df_plano = gerar_plano_anual(rota)
    
    # Salvar plano
    plano_path = DATA_DIR / "plano_turne.csv"
    df_plano.to_csv(plano_path, index=False, encoding="utf-8")
    print(f"✅ Plano salvo em: {plano_path}")
    
    # Exibir resumo
    print("\n📅 Plano de Turnê Anual:")
    print("-" * 80)
    for _, row in df_plano.iterrows():
        print(f"   {row['Mês']:12} | {row['Cidade']:30} | Score: {row['Score']:5.1f} | "
              f"Lucro: R$ {row['Lucro Potencial (R$)']:>12,.2f}")
    
    print("-" * 80)
    print(f"\n📊 Resumo da Turnê:")
    print(f"   • Lucro Total Estimado: R$ {df_plano['Lucro Potencial (R$)'].sum():,.2f}")
    print(f"   • Distância Total: {df_plano['Distância do Anterior (km)'].sum():,.0f} km")
    print(f"   • ROI Médio: {df_plano['ROI (%)'].mean():.1f}%")
    print(f"   • Score Médio: {df_plano['Score'].mean():.1f}")
    
    # Gerar planos de marketing
    print("\n📢 Gerando planos de marketing...")
    planos_marketing = []
    for show in rota:
        plano = gerar_plano_marketing(
            show["cidade"], show["mes"], show["mes_nome"]
        )
        planos_marketing.append(plano)
    
    # Salvar planos de marketing como JSON
    import json
    marketing_path = DATA_DIR / "planos_marketing.json"
    with open(marketing_path, "w", encoding="utf-8") as f:
        json.dump(planos_marketing, f, ensure_ascii=False, indent=2)
    print(f"✅ Planos de marketing salvos em: {marketing_path}")
    
    return df_plano, planos_marketing


if __name__ == "__main__":
    main()
