# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# Copyright (c) 2026 Lenon de Paula - https://github.com/lenondpaula
"""
Processador de PDFs - Assistente Corporativo RAG
Lê PDFs e divide em chunks para indexação vetorial
"""

from pathlib import Path
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

BASE_DIR = Path(__file__).resolve().parents[1]
DOCUMENTOS_DIR = BASE_DIR / "documentos"

# Configurações de chunking
CHUNK_SIZE = 1000      # Tamanho de cada pedaço em caracteres
CHUNK_OVERLAP = 100    # Sobreposição para manter contexto


def carregar_pdf(caminho_pdf: Path) -> List[Document]:
    """
    Carrega um PDF e retorna lista de documentos (uma página = um documento).
    
    Args:
        caminho_pdf: Caminho para o arquivo PDF
        
    Returns:
        Lista de Documents do LangChain
    """
    loader = PyPDFLoader(str(caminho_pdf))
    documentos = loader.load()
    
    # Adiciona metadados úteis
    for doc in documentos:
        doc.metadata["fonte"] = caminho_pdf.name
    
    return documentos


def dividir_em_chunks(documentos: List[Document]) -> List[Document]:
    """
    Divide documentos em pedaços menores para indexação.
    
    Args:
        documentos: Lista de Documents do LangChain
        
    Returns:
        Lista de chunks (Documents menores)
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    
    chunks = text_splitter.split_documents(documentos)
    
    # Adiciona ID único a cada chunk
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    
    return chunks


def processar_todos_pdfs() -> List[Document]:
    """
    Processa todos os PDFs na pasta documentos/.
    
    Returns:
        Lista de todos os chunks de todos os PDFs
    """
    todos_chunks = []
    
    # Garante que a pasta existe
    DOCUMENTOS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Processa cada PDF
    arquivos_pdf = list(DOCUMENTOS_DIR.glob("*.pdf"))
    
    if not arquivos_pdf:
        print("⚠️  Nenhum PDF encontrado na pasta documentos/")
        return []
    
    print(f"📂 Encontrados {len(arquivos_pdf)} PDFs para processar")
    
    for pdf_path in arquivos_pdf:
        print(f"   📄 Processando: {pdf_path.name}")
        
        try:
            # Carrega PDF
            documentos = carregar_pdf(pdf_path)
            print(f"      └─ {len(documentos)} páginas carregadas")
            
            # Divide em chunks
            chunks = dividir_em_chunks(documentos)
            print(f"      └─ {len(chunks)} chunks criados")
            
            todos_chunks.extend(chunks)
            
        except Exception as e:
            print(f"      ❌ Erro ao processar: {e}")
    
    return todos_chunks


def processar_pdf_upload(conteudo_bytes: bytes, nome_arquivo: str) -> List[Document]:
    """
    Processa um PDF enviado via upload (bytes em memória).
    
    Args:
        conteudo_bytes: Conteúdo do PDF em bytes
        nome_arquivo: Nome original do arquivo
        
    Returns:
        Lista de chunks do PDF
    """
    import tempfile
    
    # Salva temporariamente para o PyPDFLoader processar
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(conteudo_bytes)
        tmp_path = Path(tmp.name)
    
    try:
        # Carrega e processa
        documentos = carregar_pdf(tmp_path)
        
        # Atualiza metadados com nome real
        for doc in documentos:
            doc.metadata["fonte"] = nome_arquivo
        
        chunks = dividir_em_chunks(documentos)
        
        return chunks
        
    finally:
        # Remove arquivo temporário
        tmp_path.unlink(missing_ok=True)


def main():
    """Execução standalone para teste."""
    print("=" * 60)
    print("  PROCESSADOR DE PDFs - Assistente RAG")
    print("=" * 60)
    print()
    
    chunks = processar_todos_pdfs()
    
    if chunks:
        print()
        print(f"✅ Total: {len(chunks)} chunks prontos para indexação")
        print()
        print("📋 Preview do primeiro chunk:")
        print("-" * 40)
        print(chunks[0].page_content[:500] + "...")
        print("-" * 40)
        print(f"Metadados: {chunks[0].metadata}")
    
    return chunks


if __name__ == "__main__":
    main()
