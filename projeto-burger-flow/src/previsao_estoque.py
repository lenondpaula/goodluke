"""
Burger-Flow Intelligence - Previsão de Estoque com Prophet
Prevê demanda de hambúrgueres e calcula necessidade de insumos
"""

import pickle
from pathlib import Path

import pandas as pd
import numpy as np
from prophet import Prophet

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Conversão de vendas para insumos (por unidade vendida)
INSUMOS_POR_BURGER = {
    "Burger Clássico": {
        "pao_unidade": 1,
        "carne_gramas": 150,
        "queijo_gramas": 30,
        "alface_gramas": 20,
        "tomate_gramas": 40,
    },
    "Burger Gourmet": {
        "pao_unidade": 1,
        "carne_gramas": 200,
        "queijo_gramas": 50,
        "bacon_gramas": 40,
        "cebola_caramelizada_gramas": 30,
    },
}

# Insumos para batata frita
INSUMOS_BATATA = {
    "Batata Frita": {
        "batata_gramas": 200,
        "oleo_ml": 50,
    }
}


def carregar_vendas() -> pd.DataFrame:
    """Carrega e prepara dados de vendas para Prophet."""
    vendas_path = DATA_DIR / "vendas_burger.csv"
    
    if not vendas_path.exists():
        raise FileNotFoundError(
            f"Arquivo de vendas não encontrado: {vendas_path}\n"
            "Execute primeiro: python src/gerar_dados_burger.py"
        )
    
    df = pd.read_csv(vendas_path)
    df["data"] = pd.to_datetime(df["data"])
    return df


def preparar_dados_prophet(df: pd.DataFrame, produto: str) -> pd.DataFrame:
    """
    Prepara dados no formato esperado pelo Prophet.
    Prophet requer colunas 'ds' (datetime) e 'y' (valor).
    """
    df_produto = df[df["produto"] == produto].copy()
    df_prophet = df_produto.groupby("data")["vendas"].sum().reset_index()
    df_prophet.columns = ["ds", "y"]
    return df_prophet


def treinar_modelo_prophet(df_prophet: pd.DataFrame, produto: str) -> Prophet:
    """
    Treina modelo Prophet para um produto específico.
    
    Configuração:
    - Sazonalidade semanal (padrão sexta/sábado)
    - Sazonalidade anual (férias, inverno)
    - Intervalo de confiança de 95%
    """
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.95,
        seasonality_mode="multiplicative",
    )
    
    # Suprimir logs do Prophet
    model.fit(df_prophet)
    
    # Salvar modelo
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"prophet_{produto.lower().replace(' ', '_')}.pkl"
    model_path = MODELS_DIR / nome_arquivo
    
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    print(f"   ✓ Modelo salvo: {model_path.name}")
    return model


def prever_demanda(model: Prophet, dias: int = 7) -> pd.DataFrame:
    """Gera previsão para os próximos N dias."""
    future = model.make_future_dataframe(periods=dias)
    forecast = model.predict(future)
    
    # Retorna apenas os dias futuros
    previsao = forecast.tail(dias)[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()
    previsao.columns = ["data", "previsao", "limite_inferior", "limite_superior"]
    previsao["previsao"] = previsao["previsao"].round().astype(int).clip(lower=0)
    previsao["limite_inferior"] = previsao["limite_inferior"].round().astype(int).clip(lower=0)
    previsao["limite_superior"] = previsao["limite_superior"].round().astype(int).clip(lower=0)
    
    return previsao


def calcular_necessidade_insumos(previsoes: dict) -> pd.DataFrame:
    """
    Converte previsões de vendas em necessidade de insumos.
    
    Retorna DataFrame com quantidade de cada insumo para a semana.
    """
    insumos_totais = {}
    
    for produto, df_prev in previsoes.items():
        vendas_semana = df_prev["previsao"].sum()
        
        # Mapear insumos por produto
        if produto in INSUMOS_POR_BURGER:
            for insumo, qtd_por_unidade in INSUMOS_POR_BURGER[produto].items():
                if insumo not in insumos_totais:
                    insumos_totais[insumo] = 0
                insumos_totais[insumo] += vendas_semana * qtd_por_unidade
        
        if produto in INSUMOS_BATATA:
            for insumo, qtd_por_unidade in INSUMOS_BATATA[produto].items():
                if insumo not in insumos_totais:
                    insumos_totais[insumo] = 0
                insumos_totais[insumo] += vendas_semana * qtd_por_unidade
    
    # Criar DataFrame de insumos
    df_insumos = pd.DataFrame([
        {"insumo": k, "quantidade": v, "unidade": "g" if "gramas" in k else ("ml" if "ml" in k else "un")}
        for k, v in insumos_totais.items()
    ])
    
    # Converter gramas para kg onde aplicável
    df_insumos["quantidade_convertida"] = df_insumos.apply(
        lambda row: row["quantidade"] / 1000 if row["unidade"] == "g" else row["quantidade"],
        axis=1
    ).round(2)
    df_insumos["unidade_final"] = df_insumos["unidade"].replace({"g": "kg"})
    
    # Limpar nome do insumo
    df_insumos["insumo_limpo"] = df_insumos["insumo"].str.replace("_gramas", "").str.replace("_ml", "").str.replace("_unidade", "").str.replace("_", " ").str.title()
    
    return df_insumos[["insumo_limpo", "quantidade_convertida", "unidade_final"]].rename(
        columns={"insumo_limpo": "Insumo", "quantidade_convertida": "Quantidade", "unidade_final": "Unidade"}
    )


def main():
    """Pipeline completo de previsão de estoque."""
    print("🍔 Burger-Flow Intelligence - Previsão de Estoque")
    print("=" * 50)
    
    # Carregar dados
    print("\n📊 Carregando histórico de vendas...")
    df_vendas = carregar_vendas()
    print(f"   → {len(df_vendas):,} registros carregados")
    
    # Produtos para previsão
    produtos = ["Burger Clássico", "Burger Gourmet", "Batata Frita"]
    previsoes = {}
    
    # Treinar modelos e gerar previsões
    print("\n🔮 Treinando modelos Prophet...")
    for produto in produtos:
        print(f"\n   📦 {produto}")
        df_prophet = preparar_dados_prophet(df_vendas, produto)
        model = treinar_modelo_prophet(df_prophet, produto)
        previsao = prever_demanda(model, dias=7)
        previsoes[produto] = previsao
        print(f"      Previsão 7 dias: {previsao['previsao'].sum()} unidades")
    
    # Consolidar previsões
    print("\n📋 Consolidando previsões...")
    df_consolidado = pd.DataFrame()
    for produto, df_prev in previsoes.items():
        df_temp = df_prev.copy()
        df_temp["produto"] = produto
        df_consolidado = pd.concat([df_consolidado, df_temp], ignore_index=True)
    
    previsao_path = DATA_DIR / "previsao_estoque.csv"
    df_consolidado.to_csv(previsao_path, index=False)
    print(f"   ✓ Salvo em {previsao_path}")
    
    # Calcular necessidade de insumos
    print("\n🥩 Calculando necessidade de insumos...")
    df_insumos = calcular_necessidade_insumos(previsoes)
    insumos_path = DATA_DIR / "necessidade_insumos.csv"
    df_insumos.to_csv(insumos_path, index=False)
    print(f"   ✓ Salvo em {insumos_path}")
    
    print("\n📦 Sugestão de Pedido para a Semana:")
    print("-" * 40)
    for _, row in df_insumos.iterrows():
        print(f"   {row['Insumo']}: {row['Quantidade']} {row['Unidade']}")
    
    print("\n✅ Previsão de estoque concluída!")


if __name__ == "__main__":
    main()
