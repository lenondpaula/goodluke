"""
Verificação de ambiente para o Oráculo de Vendas
Confirma que Prophet e dependências estão instalados corretamente
"""

import sys


def verificar_dependencias():
    """Verifica se todas as dependências críticas estão instaladas."""
    dependencias = {
        "pandas": "Manipulação de dados",
        "prophet": "Modelo de séries temporais",
        "plotly": "Gráficos interativos",
        "streamlit": "Dashboard web",
        "statsmodels": "Análise estatística",
    }
    
    erros = []
    
    print("🔍 Verificando dependências do Oráculo de Vendas...\n")
    
    for pacote, descricao in dependencias.items():
        try:
            __import__(pacote)
            print(f"  ✅ {pacote}: {descricao}")
        except ImportError:
            print(f"  ❌ {pacote}: NÃO ENCONTRADO - {descricao}")
            erros.append(pacote)
    
    print()
    
    if erros:
        print(f"⚠️  Pacotes faltando: {', '.join(erros)}")
        print("   Execute: pip install -r requirements.txt")
        return False
    else:
        print("🎉 Todas as dependências instaladas corretamente!")
        return True


def verificar_prophet_detalhado():
    """Teste mais profundo do Prophet."""
    try:
        from prophet import Prophet
        import pandas as pd
        
        # Teste rápido com dados mínimos
        df_teste = pd.DataFrame({
            'ds': pd.date_range('2024-01-01', periods=10, freq='D'),
            'y': [100, 110, 105, 120, 115, 130, 125, 140, 135, 150]
        })
        
        modelo = Prophet(daily_seasonality=False, weekly_seasonality=False, yearly_seasonality=False)
        modelo.fit(df_teste)
        
        futuro = modelo.make_future_dataframe(periods=3)
        previsao = modelo.predict(futuro)
        
        print("🔮 Prophet funcionando corretamente!")
        print(f"   Previsão para próximos 3 dias: {previsao['yhat'].tail(3).values.round(2)}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Prophet: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("  ORÁCULO DE VENDAS - Verificação de Ambiente")
    print("=" * 60)
    print()
    
    deps_ok = verificar_dependencias()
    
    if deps_ok:
        print("\n" + "-" * 60)
        print("  Teste detalhado do Prophet")
        print("-" * 60 + "\n")
        verificar_prophet_detalhado()
    
    print()
