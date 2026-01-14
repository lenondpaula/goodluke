"""
GIG-Master AI - Gerador de Dados de Mercado de Shows
Simula o "calor" do público em diferentes cidades brasileiras
"""

import random
from pathlib import Path

import pandas as pd
from faker import Faker

# Configuração para reprodutibilidade
random.seed(42)
fake = Faker("pt_BR")
Faker.seed(42)

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"

# 50 Cidades Brasileiras com dados geográficos aproximados
CIDADES_BRASIL = [
    # (cidade, estado, latitude, longitude, regiao)
    ("São Paulo", "SP", -23.55, -46.63, "Sudeste"),
    ("Rio de Janeiro", "RJ", -22.91, -43.17, "Sudeste"),
    ("Belo Horizonte", "MG", -19.92, -43.94, "Sudeste"),
    ("Brasília", "DF", -15.79, -47.88, "Centro-Oeste"),
    ("Salvador", "BA", -12.97, -38.50, "Nordeste"),
    ("Fortaleza", "CE", -3.72, -38.52, "Nordeste"),
    ("Curitiba", "PR", -25.43, -49.27, "Sul"),
    ("Recife", "PE", -8.05, -34.88, "Nordeste"),
    ("Porto Alegre", "RS", -30.03, -51.23, "Sul"),
    ("Manaus", "AM", -3.10, -60.02, "Norte"),
    ("Belém", "PA", -1.46, -48.50, "Norte"),
    ("Goiânia", "GO", -16.68, -49.25, "Centro-Oeste"),
    ("Guarulhos", "SP", -23.46, -46.53, "Sudeste"),
    ("Campinas", "SP", -22.91, -47.06, "Sudeste"),
    ("São Luís", "MA", -2.53, -44.30, "Nordeste"),
    ("São Gonçalo", "RJ", -22.83, -43.05, "Sudeste"),
    ("Maceió", "AL", -9.67, -35.74, "Nordeste"),
    ("Duque de Caxias", "RJ", -22.79, -43.31, "Sudeste"),
    ("Natal", "RN", -5.79, -35.21, "Nordeste"),
    ("Teresina", "PI", -5.09, -42.80, "Nordeste"),
    ("Campo Grande", "MS", -20.47, -54.62, "Centro-Oeste"),
    ("São Bernardo do Campo", "SP", -23.69, -46.56, "Sudeste"),
    ("João Pessoa", "PB", -7.12, -34.86, "Nordeste"),
    ("Santo André", "SP", -23.67, -46.54, "Sudeste"),
    ("Osasco", "SP", -23.53, -46.79, "Sudeste"),
    ("Ribeirão Preto", "SP", -21.18, -47.81, "Sudeste"),
    ("Uberlândia", "MG", -18.92, -48.28, "Sudeste"),
    ("Contagem", "MG", -19.93, -44.05, "Sudeste"),
    ("Sorocaba", "SP", -23.50, -47.46, "Sudeste"),
    ("Aracaju", "SE", -10.91, -37.07, "Nordeste"),
    ("Feira de Santana", "BA", -12.27, -38.97, "Nordeste"),
    ("Cuiabá", "MT", -15.60, -56.10, "Centro-Oeste"),
    ("Joinville", "SC", -26.30, -48.85, "Sul"),
    ("Juiz de Fora", "MG", -21.76, -43.35, "Sudeste"),
    ("Londrina", "PR", -23.30, -51.17, "Sul"),
    ("Aparecida de Goiânia", "GO", -16.82, -49.24, "Centro-Oeste"),
    ("Niterói", "RJ", -22.88, -43.10, "Sudeste"),
    ("Porto Velho", "RO", -8.76, -63.90, "Norte"),
    ("Ananindeua", "PA", -1.37, -48.37, "Norte"),
    ("Serra", "ES", -20.13, -40.31, "Sudeste"),
    ("Florianópolis", "SC", -27.60, -48.55, "Sul"),
    ("Caxias do Sul", "RS", -29.17, -51.18, "Sul"),
    ("Macapá", "AP", 0.03, -51.05, "Norte"),
    ("Vila Velha", "ES", -20.33, -40.29, "Sudeste"),
    ("São José do Rio Preto", "SP", -20.82, -49.38, "Sudeste"),
    ("Mogi das Cruzes", "SP", -23.52, -46.19, "Sudeste"),
    ("Santos", "SP", -23.96, -46.33, "Sudeste"),
    ("Betim", "MG", -19.97, -44.20, "Sudeste"),
    ("Diadema", "SP", -23.68, -46.62, "Sudeste"),
    ("Maringá", "PR", -23.43, -51.94, "Sul"),
]

# Capitais para cálculo de distância
CAPITAIS = {
    "Sudeste": ("São Paulo", -23.55, -46.63),
    "Sul": ("Curitiba", -25.43, -49.27),
    "Nordeste": ("Salvador", -12.97, -38.50),
    "Norte": ("Manaus", -3.10, -60.02),
    "Centro-Oeste": ("Brasília", -15.79, -47.88),
}


def calcular_distancia(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula distância aproximada em km usando fórmula simplificada."""
    # Fórmula de Haversine simplificada (aproximação)
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Raio da Terra em km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def gerar_populacao(cidade: str) -> int:
    """Gera população estimada baseada na cidade."""
    # Populações aproximadas das maiores cidades
    populacoes_base = {
        "São Paulo": 12_300_000,
        "Rio de Janeiro": 6_700_000,
        "Brasília": 3_000_000,
        "Salvador": 2_900_000,
        "Fortaleza": 2_700_000,
        "Belo Horizonte": 2_500_000,
        "Manaus": 2_200_000,
        "Curitiba": 1_900_000,
        "Recife": 1_600_000,
        "Porto Alegre": 1_500_000,
    }
    
    if cidade in populacoes_base:
        # Adiciona variação de ±5%
        base = populacoes_base[cidade]
        return int(base * random.uniform(0.95, 1.05))
    else:
        # Para outras cidades, gera entre 200k e 1.5M
        return random.randint(200_000, 1_500_000)


def gerar_afinidade_musical(regiao: str) -> int:
    """Gera índice de afinidade com gênero Musical (0-100)."""
    # Diferentes regiões têm diferentes afinidades musicais
    afinidades_base = {
        "Sudeste": (60, 95),  # Alta demanda
        "Sul": (55, 90),
        "Nordeste": (65, 98),  # Muito alta demanda
        "Centro-Oeste": (50, 85),
        "Norte": (45, 80),
    }
    
    min_af, max_af = afinidades_base.get(regiao, (40, 75))
    return random.randint(min_af, max_af)


def gerar_preco_medio_ingresso(populacao: int, regiao: str) -> float:
    """Gera preço médio de ingresso baseado na cidade e região."""
    # Base de preço por região
    precos_base = {
        "Sudeste": (120, 280),
        "Sul": (100, 250),
        "Nordeste": (80, 200),
        "Centro-Oeste": (90, 220),
        "Norte": (70, 180),
    }
    
    min_preco, max_preco = precos_base.get(regiao, (80, 200))
    
    # Ajuste por população (cidades maiores = ingressos mais caros)
    fator_populacao = 1 + (populacao / 15_000_000) * 0.3
    
    preco = random.uniform(min_preco, max_preco) * fator_populacao
    return round(preco, 2)


def gerar_meses_ideais(regiao: str) -> str:
    """Retorna meses ideais para shows baseado na região (evita chuvas)."""
    meses_ideais = {
        "Sudeste": "Abr-Set",  # Evita verão chuvoso
        "Sul": "Mar-Nov",  # Evita inverno rigoroso
        "Nordeste": "Ago-Mar",  # Evita inverno chuvoso
        "Centro-Oeste": "Mai-Set",  # Evita estação chuvosa
        "Norte": "Jun-Nov",  # Evita estação chuvosa
    }
    return meses_ideais.get(regiao, "Abr-Out")


def gerar_mercado_shows() -> pd.DataFrame:
    """Gera dataset completo do mercado de shows."""
    dados = []
    
    for cidade, estado, lat, lon, regiao in CIDADES_BRASIL:
        # Calcular distância da capital mais próxima
        capital_nome, cap_lat, cap_lon = CAPITAIS[regiao]
        distancia_capital = calcular_distancia(lat, lon, cap_lat, cap_lon)
        
        # Gerar dados simulados
        populacao = gerar_populacao(cidade)
        afinidade = gerar_afinidade_musical(regiao)
        preco_medio = gerar_preco_medio_ingresso(populacao, regiao)
        meses_ideais = gerar_meses_ideais(regiao)
        
        # Capacidade média de venues (baseada em população)
        capacidade_venue = int(populacao * random.uniform(0.001, 0.003))
        capacidade_venue = max(5000, min(capacidade_venue, 50000))
        
        # Custo de produção estimado (logística, equipe, etc.)
        custo_base = 50000 + (distancia_capital * 50)  # Custo aumenta com distância
        custo_producao = round(custo_base * random.uniform(0.8, 1.3), 2)
        
        dados.append({
            "cidade": cidade,
            "estado": estado,
            "regiao": regiao,
            "latitude": lat,
            "longitude": lon,
            "populacao": populacao,
            "afinidade_musical": afinidade,
            "preco_medio_ingresso": preco_medio,
            "distancia_capital_km": round(distancia_capital, 1),
            "capital_referencia": capital_nome,
            "meses_ideais": meses_ideais,
            "capacidade_venue": capacidade_venue,
            "custo_producao_estimado": custo_producao,
        })
    
    df = pd.DataFrame(dados)
    
    # Adicionar colunas calculadas
    df["receita_potencial"] = df["preco_medio_ingresso"] * df["capacidade_venue"]
    df["lucro_potencial"] = df["receita_potencial"] - df["custo_producao_estimado"]
    
    return df


def main():
    """Função principal - gera e salva os dados."""
    print("🎸 GIG-Master AI - Gerador de Mercado de Shows")
    print("=" * 50)
    
    # Criar diretório de dados se não existir
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Gerar dados
    print("\n📊 Gerando dados de mercado para 50 cidades...")
    df = gerar_mercado_shows()
    
    # Salvar CSV
    csv_path = DATA_DIR / "mercado_shows.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"✅ Dados salvos em: {csv_path}")
    
    # Estatísticas
    print("\n📈 Estatísticas do Mercado:")
    print(f"   • Total de cidades: {len(df)}")
    print(f"   • População total alcançável: {df['populacao'].sum():,.0f}")
    print(f"   • Afinidade média: {df['afinidade_musical'].mean():.1f}/100")
    print(f"   • Preço médio de ingresso: R$ {df['preco_medio_ingresso'].mean():.2f}")
    print(f"   • Lucro potencial total: R$ {df['lucro_potencial'].sum():,.2f}")
    
    # Top 5 cidades por potencial
    print("\n🏆 Top 5 Cidades por Lucro Potencial:")
    top5 = df.nlargest(5, "lucro_potencial")[["cidade", "estado", "lucro_potencial"]]
    for i, row in top5.iterrows():
        print(f"   {row['cidade']}/{row['estado']}: R$ {row['lucro_potencial']:,.2f}")
    
    return df


if __name__ == "__main__":
    main()
