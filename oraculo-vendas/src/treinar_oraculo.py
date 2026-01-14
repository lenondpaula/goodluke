# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Treinamento do Modelo Oráculo - Séries Temporais com Prophet
Treina um modelo Prophet para previsão de vendas dos próximos 30 dias
"""

from pathlib import Path
import pickle
import pandas as pd
from prophet import Prophet

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "vendas_historico.csv"
MODEL_PATH = BASE_DIR / "models" / "prophet_model.pkl"


def carregar_dados() -> pd.DataFrame:
    """Carrega o histórico de vendas."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo de dados não encontrado: {DATA_PATH}\n"
            "Execute primeiro: python src/gerar_vendas.py"
        )
    
    df = pd.read_csv(DATA_PATH)
    df['ds'] = pd.to_datetime(df['ds'])
    return df


def treinar_modelo(df: pd.DataFrame) -> Prophet:
    """
    Treina o modelo Prophet com os dados históricos.
    
    Configurações:
    - Sazonalidade diária: Desativada (dados agregados por dia)
    - Sazonalidade semanal: Ativada (padrão fim de semana)
    - Sazonalidade anual: Ativada (padrão Natal/meses)
    """
    
    print("🔮 Configurando o Oráculo (Prophet)...")
    
    modelo = Prophet(
        daily_seasonality=False,   # Dados já são diários agregados
        weekly_seasonality=True,   # Captura padrão de fim de semana
        yearly_seasonality=True,   # Captura sazonalidade anual (Natal, etc)
        seasonality_mode='multiplicative',  # Melhor para vendas (% de variação)
        interval_width=0.95,       # Intervalo de confiança de 95%
    )
    
    # Adiciona feriados brasileiros importantes
    modelo.add_country_holidays(country_name='BR')
    
    print("📚 Treinando com dados históricos...")
    modelo.fit(df)
    print("   ✅ Modelo treinado!")
    
    return modelo


def gerar_previsao(modelo: Prophet, dias_futuro: int = 30) -> pd.DataFrame:
    """Gera previsão para os próximos N dias."""
    
    print(f"🔮 Gerando previsão para os próximos {dias_futuro} dias...")
    
    # Cria dataframe com datas futuras
    futuro = modelo.make_future_dataframe(periods=dias_futuro)
    
    # Gera previsão
    previsao = modelo.predict(futuro)
    
    print("   ✅ Previsão gerada!")
    
    return previsao


def salvar_modelo(modelo: Prophet):
    """Salva o modelo treinado em pickle."""
    
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(modelo, f)
    
    print(f"💾 Modelo salvo em: {MODEL_PATH}")


def main():
    """Pipeline principal de treinamento."""
    
    print("=" * 60)
    print("  ORÁCULO DE VENDAS - Treinamento do Modelo")
    print("=" * 60)
    print()
    
    # 1. Carrega dados
    print("📂 Carregando dados históricos...")
    df = carregar_dados()
    print(f"   {len(df):,} registros carregados")
    print(f"   Período: {df['ds'].min().date()} a {df['ds'].max().date()}")
    print()
    
    # 2. Treina modelo
    modelo = treinar_modelo(df)
    print()
    
    # 3. Gera previsão de teste
    previsao = gerar_previsao(modelo, dias_futuro=30)
    print()
    
    # 4. Estatísticas da previsão
    previsao_futura = previsao.tail(30)
    print("📊 Previsão para os próximos 30 dias:")
    print(f"   Venda total prevista: R$ {previsao_futura['yhat'].sum():,.2f}")
    print(f"   Média diária prevista: R$ {previsao_futura['yhat'].mean():,.2f}")
    print(f"   Intervalo de confiança:")
    print(f"     - Pessimista: R$ {previsao_futura['yhat_lower'].sum():,.2f}")
    print(f"     - Otimista: R$ {previsao_futura['yhat_upper'].sum():,.2f}")
    print()
    
    # 5. Salva modelo
    salvar_modelo(modelo)
    
    print()
    print("🎉 Treinamento concluído com sucesso!")
    print("   Execute o dashboard: streamlit run app/dashboard_vendas.py")
    
    return modelo, previsao


if __name__ == "__main__":
    main()
