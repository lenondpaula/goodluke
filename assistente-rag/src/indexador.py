# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Indexador Vetorial - Assistente Corporativo RAG
Transforma chunks de texto em embeddings e armazena no ChromaDB
"""

from pathlib import Path
from typing import List, Optional
import sqlite3
import shutil
import os
import tempfile

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

BASE_DIR = Path(__file__).resolve().parents[1]

# Detecta Streamlit Cloud: filesystem é readonly exceto /tmp
# Variáveis que indicam ambiente cloud: HOME=/home/adminuser ou mount path /mount/src
_is_cloud = (
    os.getenv("HOME") == "/home/adminuser"
    or str(BASE_DIR).startswith("/mount/src")
    or not os.access(str(BASE_DIR), os.W_OK)
)

if _is_cloud:
    DB_DIR = Path(tempfile.gettempdir()) / "assistente_rag_db"
else:
    DB_DIR = BASE_DIR / "db_store"

COLLECTION_NAME = "documentos_corporativos"

# Modelo de embeddings gratuito e leve (roda no CPU)
# all-MiniLM-L6-v2: 384 dimensões, ~80MB, bom equilíbrio velocidade/qualidade
MODELO_EMBEDDINGS = "sentence-transformers/all-MiniLM-L6-v2"


def criar_embeddings():
    """
    Cria instância do modelo de embeddings HuggingFace.
    Roda localmente, sem necessidade de API.
    """
    import streamlit as st
    
    @st.cache_resource(show_spinner=False)
    def _load_embeddings():
        return HuggingFaceEmbeddings(
            model_name=MODELO_EMBEDDINGS,
            model_kwargs={
                'device': 'cpu',
                'trust_remote_code': True
            },
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 32
            }
        )
    
    return _load_embeddings()


def criar_ou_carregar_vectorstore(embeddings=None) -> Chroma:
    """
    Cria nova base vetorial ou carrega existente.
    
    Args:
        embeddings: Modelo de embeddings (cria novo se None)
        
    Returns:
        Instância do ChromaDB
    """
    if embeddings is None:
        embeddings = criar_embeddings()
    
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(DB_DIR),
    )

    try:
        # Força acesso à coleção para validar o schema do DB
        _ = vectorstore._collection.count()
    except Exception as exc:
        mensagem = str(exc).lower()
        erro_schema = (
            "no such table: embeddings" in mensagem
            or "error executing plan" in mensagem
            or isinstance(exc, sqlite3.OperationalError)
        )
        if erro_schema:
            if DB_DIR.exists():
                shutil.rmtree(DB_DIR)
                DB_DIR.mkdir(parents=True, exist_ok=True)
            vectorstore = Chroma(
                collection_name=COLLECTION_NAME,
                embedding_function=embeddings,
                persist_directory=str(DB_DIR),
            )
        else:
            raise

    return vectorstore


def indexar_documentos(chunks: List[Document], limpar_base: bool = False) -> Chroma:
    """
    Indexa lista de chunks no ChromaDB.
    
    Args:
        chunks: Lista de Documents para indexar
        limpar_base: Se True, limpa a base antes de indexar
        
    Returns:
        Instância do ChromaDB com documentos indexados
    """
    if not chunks:
        print("⚠️  Nenhum chunk para indexar")
        return criar_ou_carregar_vectorstore()
    
    print(f"🔮 Criando embeddings para {len(chunks)} chunks...")
    embeddings = criar_embeddings()
    
    if limpar_base:
        # Remove base existente
        import shutil
        if DB_DIR.exists():
            shutil.rmtree(DB_DIR)
            print("   🗑️  Base anterior removida")
    
    print("📦 Indexando no ChromaDB...")
    
    # Cria vectorstore com os documentos
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(DB_DIR),
    )
    
    print(f"✅ {len(chunks)} chunks indexados com sucesso!")
    
    return vectorstore


def buscar_similares(query: str, k: int = 3, vectorstore: Optional[Chroma] = None) -> List[Document]:
    """
    Busca os k documentos mais similares à query.
    
    Args:
        query: Texto da pergunta/busca
        k: Número de resultados a retornar
        vectorstore: Instância do ChromaDB (carrega se None)
        
    Returns:
        Lista dos k Documents mais relevantes
    """
    if vectorstore is None:
        vectorstore = criar_ou_carregar_vectorstore()
    
    # Verifica se há documentos na base
    if vectorstore._collection.count() == 0:
        print("⚠️  Base vetorial vazia. Indexe documentos primeiro.")
        return []
    
    resultados = vectorstore.similarity_search(query, k=k)
    
    return resultados


def buscar_com_scores(query: str, k: int = 3, vectorstore: Optional[Chroma] = None) -> List[tuple]:
    """
    Busca similares retornando também os scores de similaridade.
    
    Args:
        query: Texto da pergunta/busca
        k: Número de resultados
        vectorstore: Instância do ChromaDB
        
    Returns:
        Lista de tuplas (Document, score)
    """
    if vectorstore is None:
        vectorstore = criar_ou_carregar_vectorstore()

    try:
        if vectorstore._collection.count() == 0:
            return []
        resultados = vectorstore.similarity_search_with_score(query, k=k)
        return resultados
    except Exception:
        # Se o DB estiver inválido, tenta recriar vazio e retorna sem resultados
        vectorstore = criar_ou_carregar_vectorstore()
        try:
            if vectorstore._collection.count() == 0:
                return []
            return vectorstore.similarity_search_with_score(query, k=k)
        except Exception:
            return []


def contar_documentos(vectorstore: Optional[Chroma] = None) -> int:
    """Retorna o número de documentos indexados."""
    if vectorstore is None:
        vectorstore = criar_ou_carregar_vectorstore()

    try:
        return vectorstore._collection.count()
    except Exception:
        # Tenta recriar o DB se estiver corrompido
        vectorstore = criar_ou_carregar_vectorstore()
        try:
            return vectorstore._collection.count()
        except Exception:
            return 0


def main():
    """Pipeline completo: processa PDFs e indexa."""
    from processador_pdf import processar_todos_pdfs
    
    print("=" * 60)
    print("  INDEXADOR VETORIAL - Assistente RAG")
    print("=" * 60)
    print()
    
    # 1. Processa PDFs
    chunks = processar_todos_pdfs()
    
    if not chunks:
        print("\n⚠️  Coloque PDFs na pasta documentos/ e execute novamente.")
        return
    
    print()
    
    # 2. Indexa no ChromaDB
    vectorstore = indexar_documentos(chunks, limpar_base=True)
    
    print()
    print(f"📊 Total de documentos na base: {contar_documentos(vectorstore)}")
    
    # 3. Teste de busca
    print()
    print("🔍 Teste de busca semântica:")
    print("-" * 40)
    
    query_teste = "Qual é o objetivo principal do documento?"
    resultados = buscar_similares(query_teste, k=2, vectorstore=vectorstore)
    
    print(f"Query: '{query_teste}'")
    print()
    
    for i, doc in enumerate(resultados, 1):
        print(f"Resultado {i}:")
        print(f"  Fonte: {doc.metadata.get('fonte', 'N/A')}")
        print(f"  Trecho: {doc.page_content[:200]}...")
        print()
    
    print("✅ Indexação concluída! Pronto para o chatbot.")


if __name__ == "__main__":
    main()
