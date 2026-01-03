"""
Motor de Análise de Sentimentos - TechNova
Utiliza TextBlob para classificar polaridade de comentários
"""

import pandas as pd
from textblob import TextBlob
import os
from typing import Tuple

def analisar_sentimento(texto: str) -> Tuple[float, str]:
    """
    Analisa o sentimento de um texto usando TextBlob.
    
    Args:
        texto: String com o texto a ser analisado
        
    Returns:
        Tuple contendo:
        - polaridade: float de -1 (muito negativo) a 1 (muito positivo)
        - classificacao: 'Positivo', 'Negativo' ou 'Neutro'
    """
    try:
        # Cria objeto TextBlob
        blob = TextBlob(str(texto))
        
        # Obtém polaridade (-1 a 1)
        polaridade = blob.sentiment.polarity
        
        # Classifica baseado na polaridade
        if polaridade > 0.1:
            classificacao = 'Positivo'
        elif polaridade < -0.1:
            classificacao = 'Negativo'
        else:
            classificacao = 'Neutro'
            
        return polaridade, classificacao
        
    except Exception as e:
        print(f"Erro ao analisar texto: {e}")
        return 0.0, 'Neutro'

def analisar_subjetividade(texto: str) -> float:
    """
    Analisa a subjetividade de um texto.
    
    Args:
        texto: String com o texto a ser analisado
        
    Returns:
        subjetividade: float de 0 (objetivo) a 1 (subjetivo)
    """
    try:
        blob = TextBlob(str(texto))
        return blob.sentiment.subjectivity
    except Exception:
        return 0.5

def processar_dataframe(df: pd.DataFrame, coluna_texto: str = 'texto') -> pd.DataFrame:
    """
    Processa um DataFrame aplicando análise de sentimentos.
    
    Args:
        df: DataFrame com os dados
        coluna_texto: Nome da coluna com o texto a analisar
        
    Returns:
        DataFrame com colunas adicionais de polaridade e classificação
    """
    print("🔍 Iniciando análise de sentimentos...")
    
    # Aplica análise de sentimentos
    resultados = df[coluna_texto].apply(analisar_sentimento)
    
    # Separa polaridade e classificação
    df['polaridade'] = resultados.apply(lambda x: x[0])
    df['classificacao'] = resultados.apply(lambda x: x[1])
    
    # Adiciona subjetividade
    df['subjetividade'] = df[coluna_texto].apply(analisar_subjetividade)
    
    print(f"✅ {len(df)} textos analisados!")
    
    return df

def gerar_estatisticas(df: pd.DataFrame) -> dict:
    """
    Gera estatísticas da análise de sentimentos.
    
    Args:
        df: DataFrame com análise já aplicada
        
    Returns:
        Dicionário com estatísticas
    """
    total = len(df)
    
    stats = {
        'total': total,
        'positivos': len(df[df['classificacao'] == 'Positivo']),
        'negativos': len(df[df['classificacao'] == 'Negativo']),
        'neutros': len(df[df['classificacao'] == 'Neutro']),
        'polaridade_media': df['polaridade'].mean(),
        'subjetividade_media': df['subjetividade'].mean(),
    }
    
    stats['pct_positivos'] = (stats['positivos'] / total) * 100
    stats['pct_negativos'] = (stats['negativos'] / total) * 100
    stats['pct_neutros'] = (stats['neutros'] / total) * 100
    
    return stats

def main():
    """Função principal para processar os comentários."""
    
    # Caminhos dos arquivos
    arquivo_entrada = 'data/comentarios_social.csv'
    arquivo_saida = 'data/comentarios_classificados.csv'
    
    # Verifica se arquivo de entrada existe
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Arquivo '{arquivo_entrada}' não encontrado!")
        print("   Execute primeiro: python src/gerador_dados.py")
        return
    
    # Carrega dados
    print(f"📂 Carregando dados de '{arquivo_entrada}'...")
    df = pd.read_csv(arquivo_entrada)
    
    # Processa análise de sentimentos
    df = processar_dataframe(df, 'texto')
    
    # Gera estatísticas
    stats = gerar_estatisticas(df)
    
    # Exibe resumo
    print("\n" + "="*50)
    print("📊 RESUMO DA ANÁLISE DE SENTIMENTOS")
    print("="*50)
    print(f"Total de comentários: {stats['total']}")
    print(f"✅ Positivos: {stats['positivos']} ({stats['pct_positivos']:.1f}%)")
    print(f"❌ Negativos: {stats['negativos']} ({stats['pct_negativos']:.1f}%)")
    print(f"➖ Neutros: {stats['neutros']} ({stats['pct_neutros']:.1f}%)")
    print(f"\n📈 Polaridade média: {stats['polaridade_media']:.3f}")
    print(f"💭 Subjetividade média: {stats['subjetividade_media']:.3f}")
    print("="*50)
    
    # Salva resultado
    df.to_csv(arquivo_saida, index=False)
    print(f"\n💾 Dados classificados salvos em '{arquivo_saida}'")
    
    return df

if __name__ == "__main__":
    main()
