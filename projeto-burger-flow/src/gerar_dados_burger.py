# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Burger-Flow Intelligence - Gerador de Dados Sintéticos
Simula histórico de vendas de hamburgueria com sazonalidade semanal
"""

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# Configuração para reprodutibilidade
random.seed(42)
np.random.seed(42)

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def gerar_vendas_historico(anos: int = 2) -> pd.DataFrame:
    """
    Gera histórico de vendas diárias para 3 produtos.
    
    Sazonalidade implementada:
    - Sexta e Sábado: +50% nas vendas
    - Domingo: +20% nas vendas
    - Dezembro/Janeiro: -15% (férias)
    - Junho/Julho: +10% (inverno = mais hambúrguer)
    """
    produtos = {
        "Burger Clássico": {"base_vendas": 45, "variacao": 12},
        "Burger Gourmet": {"base_vendas": 25, "variacao": 8},
        "Batata Frita": {"base_vendas": 60, "variacao": 15},
    }
    
    # Data inicial: 2 anos atrás
    data_inicio = datetime.now() - timedelta(days=365 * anos)
    datas = [data_inicio + timedelta(days=i) for i in range(365 * anos)]
    
    registros = []
    
    for data in datas:
        dia_semana = data.weekday()  # 0=Segunda, 6=Domingo
        mes = data.month
        
        # Fatores sazonais
        fator_dia = 1.0
        if dia_semana == 4:  # Sexta
            fator_dia = 1.5
        elif dia_semana == 5:  # Sábado
            fator_dia = 1.5
        elif dia_semana == 6:  # Domingo
            fator_dia = 1.2
        
        # Sazonalidade mensal
        fator_mes = 1.0
        if mes in [12, 1]:  # Férias de verão
            fator_mes = 0.85
        elif mes in [6, 7]:  # Inverno
            fator_mes = 1.10
        
        for produto, config in produtos.items():
            base = config["base_vendas"]
            variacao = config["variacao"]
            
            # Vendas com sazonalidade + ruído
            vendas = int(
                base * fator_dia * fator_mes 
                + np.random.normal(0, variacao)
            )
            vendas = max(0, vendas)  # Não pode ser negativo
            
            registros.append({
                "data": data.strftime("%Y-%m-%d"),
                "produto": produto,
                "vendas": vendas,
                "dia_semana": data.strftime("%A"),
            })
    
    df = pd.DataFrame(registros)
    return df


def gerar_menu_performance() -> pd.DataFrame:
    """
    Gera dados de performance do menu para análise BCG.
    
    Estrutura para identificar:
    - Estrelas: Alta Margem + Alto Volume
    - Vacas Leiteiras: Baixa Margem + Alto Volume  
    - Oportunidades: Alta Margem + Baixo Volume
    - Cães: Baixa Margem + Baixo Volume
    """
    menu_items = [
        # Estrelas (Alta Margem, Alto Volume)
        {"Item": "Burger Clássico", "Custo_Producao": 8.50, "Preco_Venda": 24.90, "Volume_Vendas": 1250},
        {"Item": "Combo Família", "Custo_Producao": 35.00, "Preco_Venda": 89.90, "Volume_Vendas": 380},
        
        # Vacas Leiteiras (Baixa Margem, Alto Volume)
        {"Item": "Batata Frita", "Custo_Producao": 4.50, "Preco_Venda": 12.90, "Volume_Vendas": 1800},
        {"Item": "Refrigerante", "Custo_Producao": 2.80, "Preco_Venda": 7.90, "Volume_Vendas": 2100},
        
        # Oportunidades (Alta Margem, Baixo Volume)
        {"Item": "Burger Gourmet", "Custo_Producao": 15.00, "Preco_Venda": 42.90, "Volume_Vendas": 180},
        {"Item": "Milkshake Premium", "Custo_Producao": 6.00, "Preco_Venda": 22.90, "Volume_Vendas": 95},
        {"Item": "Burger Vegano", "Custo_Producao": 12.00, "Preco_Venda": 36.90, "Volume_Vendas": 65},
        
        # Cães (Baixa Margem, Baixo Volume) - Candidatos a remoção
        {"Item": "Salada Caesar", "Custo_Producao": 9.00, "Preco_Venda": 18.90, "Volume_Vendas": 45},
        {"Item": "Wrap Light", "Custo_Producao": 10.00, "Preco_Venda": 19.90, "Volume_Vendas": 30},
        {"Item": "Suco Natural", "Custo_Producao": 5.50, "Preco_Venda": 11.90, "Volume_Vendas": 55},
    ]
    
    df = pd.DataFrame(menu_items)
    
    # Calcular métricas derivadas
    df["Margem_Bruta"] = df["Preco_Venda"] - df["Custo_Producao"]
    df["Margem_Percentual"] = ((df["Preco_Venda"] - df["Custo_Producao"]) / df["Preco_Venda"] * 100).round(1)
    df["Receita_Total"] = df["Preco_Venda"] * df["Volume_Vendas"]
    df["Lucro_Total"] = df["Margem_Bruta"] * df["Volume_Vendas"]
    
    return df


def classificar_quadrante_bcg(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classifica itens do menu nos quadrantes BCG adaptado.
    
    Usa medianas como thresholds para divisão em quadrantes.
    """
    mediana_volume = df["Volume_Vendas"].median()
    mediana_margem = df["Margem_Percentual"].median()
    
    def classificar(row):
        alto_volume = row["Volume_Vendas"] >= mediana_volume
        alta_margem = row["Margem_Percentual"] >= mediana_margem
        
        if alta_margem and alto_volume:
            return "⭐ Estrela"
        elif alta_margem and not alto_volume:
            return "🎯 Oportunidade"
        elif not alta_margem and alto_volume:
            return "🐄 Vaca Leiteira"
        else:
            return "🐕 Cão/Retirar"
    
    df["Classificacao_BCG"] = df.apply(classificar, axis=1)
    return df


def main():
    """Gera todos os datasets do Burger-Flow."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print("🍔 Burger-Flow Intelligence - Gerador de Dados")
    print("=" * 50)
    
    # 1. Gerar histórico de vendas
    print("\n📊 Gerando histórico de vendas (2 anos)...")
    df_vendas = gerar_vendas_historico(anos=2)
    vendas_path = DATA_DIR / "vendas_burger.csv"
    df_vendas.to_csv(vendas_path, index=False)
    print(f"   ✓ Salvo em {vendas_path}")
    print(f"   → {len(df_vendas):,} registros | {df_vendas['data'].nunique()} dias")
    
    # 2. Gerar performance do menu
    print("\n📋 Gerando performance do menu...")
    df_menu = gerar_menu_performance()
    df_menu = classificar_quadrante_bcg(df_menu)
    menu_path = DATA_DIR / "menu_performance.csv"
    df_menu.to_csv(menu_path, index=False)
    print(f"   ✓ Salvo em {menu_path}")
    print(f"   → {len(df_menu)} itens no cardápio")
    
    # Resumo por classificação BCG
    print("\n📈 Distribuição BCG:")
    for classe in df_menu["Classificacao_BCG"].unique():
        count = len(df_menu[df_menu["Classificacao_BCG"] == classe])
        print(f"   {classe}: {count} itens")
    
    print("\n✅ Dados gerados com sucesso!")


if __name__ == "__main__":
    main()
