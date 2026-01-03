"""
Setup NLTK - Download dos corpora necessários para o TextBlob
Execute este script após instalar as dependências:
    python setup_nltk.py
"""

import nltk
import ssl

def setup_nltk():
    """
    Faz o download dos corpora necessários do NLTK para o funcionamento do TextBlob.
    - punkt: tokenizador de sentenças
    - stopwords: palavras comuns que podem ser filtradas
    - punkt_tab: versão atualizada do punkt
    """
    print("🔧 Configurando NLTK para análise de sentimentos...")
    
    # Tenta contornar problemas de SSL em alguns ambientes
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Lista de corpora necessários
    corpora = ['punkt', 'punkt_tab', 'stopwords', 'brown', 'averaged_perceptron_tagger']
    
    for corpus in corpora:
        try:
            print(f"📥 Baixando '{corpus}'...")
            nltk.download(corpus, quiet=True)
            print(f"✅ '{corpus}' instalado com sucesso!")
        except Exception as e:
            print(f"⚠️ Erro ao baixar '{corpus}': {e}")
    
    print("\n🎉 Setup do NLTK concluído!")
    print("Você pode agora executar a análise de sentimentos.")

if __name__ == "__main__":
    setup_nltk()
