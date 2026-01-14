# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Visual-On-Demand — Gerador de Talentos (Fotógrafos)
Cria base de dados sintética de fotógrafos com estilos visuais distintos
"""

import random
from pathlib import Path

import pandas as pd
from faker import Faker

# Configuração para reprodutibilidade
random.seed(42)
fake = Faker("pt_BR")
Faker.seed(42)

# Diretório base
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Constantes de domínio
ESTILOS_VISUAIS = ["Dark_Moody", "Bright_Airy", "Black_White", "Vibrant_Colors"]
EQUIPAMENTOS = ["Sony Alpha", "Canon EOS R", "Nikon Z", "Fujifilm X", "Leica Q"]
ESPECIALIDADES = [
    "Casamentos", "Corporativo", "Moda", "Produtos", 
    "Retratos", "Eventos", "Arquitetura", "Gastronomia"
]

def gerar_fotografos(n: int = 50) -> pd.DataFrame:
    """
    Gera uma base de dados de fotógrafos fictícios.
    
    Args:
        n: Número de fotógrafos a gerar
        
    Returns:
        DataFrame com perfis de fotógrafos
    """
    fotografos = []
    
    for i in range(1, n + 1):
        nome = fake.name()
        slug = nome.lower().replace(" ", "-").replace(".", "")
        
        # Estilo visual dominante (assinatura do fotógrafo)
        estilo = random.choice(ESTILOS_VISUAIS)
        
        # Preço varia conforme experiência (avaliação)
        avaliacao = round(random.uniform(4.0, 5.0), 1)
        base_preco = random.randint(150, 500)
        preco_ajustado = int(base_preco * (1 + (avaliacao - 4.0) * 0.3))
        
        fotografo = {
            "ID": f"FOT-{i:04d}",
            "Nome": nome,
            "Especialidade": random.choice(ESPECIALIDADES),
            "Estilo_Dominante": estilo,
            "Equipamento": random.choice(EQUIPAMENTOS),
            "Preco_Hora": preco_ajustado,
            "Avaliacao": avaliacao,
            "Projetos_Concluidos": random.randint(20, 500),
            "Tempo_Resposta_Horas": random.randint(1, 24),
            "Link_Portfolio": f"https://portfolio.visualondemand.com/{slug}",
            "Instagram": f"@{slug.replace('-', '_')[:15]}",
            "Cidade": fake.city(),
            "Disponivel": random.choice([True, True, True, False])  # 75% disponíveis
        }
        fotografos.append(fotografo)
    
    return pd.DataFrame(fotografos)


def gerar_estilos_referencia() -> pd.DataFrame:
    """
    Gera uma tabela de referência de estilos visuais com características.
    """
    estilos = [
        {
            "Estilo": "Dark_Moody",
            "Descricao": "Tons escuros, sombras profundas, atmosfera dramática",
            "Paleta": "Pretos, marrons, tons terrosos",
            "Iluminacao": "Baixa, contrastada",
            "Ideal_Para": "Casamentos intimistas, moda editorial, retratos artísticos",
            "Keywords": "moody,dark,shadows,dramatic,cinematic,film,noir"
        },
        {
            "Estilo": "Bright_Airy",
            "Descricao": "Tons claros, muita luz natural, sensação leve e feliz",
            "Paleta": "Brancos, pastéis, tons suaves",
            "Iluminacao": "Alta, natural, difusa",
            "Ideal_Para": "Casamentos ao ar livre, lifestyle, maternidade",
            "Keywords": "bright,airy,light,natural,soft,romantic,dreamy"
        },
        {
            "Estilo": "Black_White",
            "Descricao": "Fotografia clássica em preto e branco, foco em texturas e emoções",
            "Paleta": "Escala de cinzas, alto contraste",
            "Iluminacao": "Variada, foco em contraste",
            "Ideal_Para": "Retratos, documentários, arte, arquitetura",
            "Keywords": "bw,blackwhite,monochrome,classic,timeless,artistic"
        },
        {
            "Estilo": "Vibrant_Colors",
            "Descricao": "Cores saturadas e vibrantes, energia e alegria",
            "Paleta": "Cores primárias intensas, neon",
            "Iluminacao": "Forte, colorida",
            "Ideal_Para": "Festas, eventos corporativos, produtos, moda street",
            "Keywords": "vibrant,colorful,saturated,bold,pop,energetic,fun"
        }
    ]
    return pd.DataFrame(estilos)


def main():
    """Executa a geração de dados."""
    print("🎨 Visual-On-Demand — Gerador de Talentos")
    print("=" * 50)
    
    # Gerar fotógrafos
    print("\n📸 Gerando base de fotógrafos...")
    df_fotografos = gerar_fotografos(50)
    
    path_fotografos = DATA_DIR / "fotografos.csv"
    df_fotografos.to_csv(path_fotografos, index=False)
    print(f"   ✅ {len(df_fotografos)} fotógrafos salvos em {path_fotografos}")
    
    # Estatísticas por estilo
    print("\n📊 Distribuição por Estilo Visual:")
    for estilo, count in df_fotografos["Estilo_Dominante"].value_counts().items():
        print(f"   • {estilo}: {count} fotógrafos")
    
    # Gerar referência de estilos
    print("\n🎨 Gerando tabela de referência de estilos...")
    df_estilos = gerar_estilos_referencia()
    
    path_estilos = DATA_DIR / "estilos_referencia.csv"
    df_estilos.to_csv(path_estilos, index=False)
    print(f"   ✅ Referência de estilos salva em {path_estilos}")
    
    # Preço médio por estilo
    print("\n💰 Preço Médio por Estilo:")
    preco_medio = df_fotografos.groupby("Estilo_Dominante")["Preco_Hora"].mean()
    for estilo, preco in preco_medio.items():
        print(f"   • {estilo}: R$ {preco:.2f}/hora")
    
    print("\n✨ Geração concluída com sucesso!")


if __name__ == "__main__":
    main()
