# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Gerador de Dados de Vendas - Oráculo de Vendas
Gera histórico de vendas diárias com padrões realistas:
- Tendência de crescimento anual de 10%
- Sazonalidade semanal (30% maior nos fins de semana)
- Pico de vendas em Dezembro (Natal)
- Variações aleatórias controladas
"""

from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Seed fixo para reprodutibilidade
np.random.seed(42)

# Configurações
ANOS_HISTORICO = 3
VENDA_BASE_DIARIA = 5000  # Valor base de vendas diárias
CRESCIMENTO_ANUAL = 0.10  # 10% ao ano
BOOST_FIM_SEMANA = 0.30   # 30% mais nos fins de semana
BOOST_DEZEMBRO = 0.50     # 50% mais em Dezembro (Natal)
VARIACAO_ALEATORIA = 0.15  # 15% de variação aleatória

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_PATH = DATA_DIR / "vendas_historico.csv"


def gerar_vendas_historico(anos: int = ANOS_HISTORICO) -> pd.DataFrame:
    """
    Gera histórico de vendas diárias com padrões sazonais.
    
    Args:
        anos: Número de anos de histórico
        
    Returns:
        DataFrame com colunas 'ds' (data) e 'y' (vendas)
    """
    
    # Período: últimos N anos até hoje
    data_fim = datetime.now().date()
    data_inicio = data_fim - timedelta(days=365 * anos)
    
    datas = pd.date_range(start=data_inicio, end=data_fim, freq='D')
    n_dias = len(datas)
    
    vendas = []
    
    for i, data in enumerate(datas):
        # Base com tendência de crescimento
        dias_desde_inicio = i
        fator_tendencia = 1 + (CRESCIMENTO_ANUAL * dias_desde_inicio / 365)
        venda_base = VENDA_BASE_DIARIA * fator_tendencia
        
        # Sazonalidade semanal (fim de semana = sábado e domingo)
        dia_semana = data.dayofweek
        if dia_semana >= 5:  # Sábado = 5, Domingo = 6
            venda_base *= (1 + BOOST_FIM_SEMANA)
        
        # Sazonalidade mensal (Dezembro = mês 12)
        if data.month == 12:
            # Intensifica conforme se aproxima do Natal
            dia_mes = data.day
            if dia_mes <= 24:
                intensidade_natal = (dia_mes / 24) * BOOST_DEZEMBRO
            else:
                # Após Natal, declínio gradual
                intensidade_natal = BOOST_DEZEMBRO * (1 - (dia_mes - 24) / 7)
            venda_base *= (1 + max(intensidade_natal, 0))
        
        # Sazonalidade de outros meses
        # Janeiro baixo (pós-festas), Junho/Julho baixos (inverno no Brasil)
        if data.month == 1:
            venda_base *= 0.85
        elif data.month in [6, 7]:
            venda_base *= 0.90
        elif data.month == 11:  # Black Friday
            if data.day >= 20:
                venda_base *= 1.25
        
        # Variação aleatória
        variacao = np.random.uniform(-VARIACAO_ALEATORIA, VARIACAO_ALEATORIA)
        venda_final = venda_base * (1 + variacao)
        
        vendas.append(max(venda_final, 0))  # Não permitir vendas negativas
    
    df = pd.DataFrame({
        'ds': datas,
        'y': np.array(vendas).round(2)
    })
    
    return df


def main():
    """Gera e salva o histórico de vendas."""
    
    print("📊 Gerando histórico de vendas para o Oráculo...")
    print(f"   Período: {ANOS_HISTORICO} anos")
    print(f"   Venda base diária: R$ {VENDA_BASE_DIARIA:,.2f}")
    print(f"   Crescimento anual: {CRESCIMENTO_ANUAL*100:.0f}%")
    print()
    
    # Gera dados
    df = gerar_vendas_historico(ANOS_HISTORICO)
    
    # Cria diretório se não existir
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Salva CSV
    df.to_csv(OUTPUT_PATH, index=False)
    
    # Estatísticas
    print(f"✅ Dados salvos em: {OUTPUT_PATH}")
    print()
    print("📈 Estatísticas do histórico:")
    print(f"   Total de dias: {len(df):,}")
    print(f"   Período: {df['ds'].min().date()} a {df['ds'].max().date()}")
    print(f"   Venda média: R$ {df['y'].mean():,.2f}")
    print(f"   Venda mínima: R$ {df['y'].min():,.2f}")
    print(f"   Venda máxima: R$ {df['y'].max():,.2f}")
    print(f"   Venda total: R$ {df['y'].sum():,.2f}")
    
    # Preview dos dados
    print()
    print("📋 Preview dos dados:")
    print(df.head(10).to_string(index=False))
    
    return df


if __name__ == "__main__":
    main()
