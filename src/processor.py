"""
Jornal-Agent - Processador de PDF.

Este módulo implementa a extração de texto de PDFs,
aplicação de OCR quando necessário e integração com o LLM
para geração de clipagem.

Funcionalidades:
- Extração de texto nativo com PyMuPDF
- OCR com pytesseract para páginas sem texto
- Validação de confiança por página
- Geração de arquivos de saída (TXT, JSON)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import io

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
from loguru import logger

from src.config import Config
from src.llm_client import PageContent, summarize_pages, LLMError


class ProcessingError(Exception):
    """Erro durante o processamento do PDF."""
    pass


class OCRError(Exception):
    """Erro durante o OCR."""
    pass


def get_output_filename(prefix: str, extension: str) -> str:
    """
    Gera nome de arquivo de saída com data.
    
    Args:
        prefix: Prefixo do arquivo (ex: 'clipagem')
        extension: Extensão do arquivo (ex: 'txt')
        
    Returns:
        Nome do arquivo no formato prefix-YYYYMMDD.extension
    """
    today = datetime.now().strftime("%Y%m%d")
    return f"{prefix}-{today}.{extension}"


def extract_text_from_page(page: fitz.Page) -> tuple[str, bool]:
    """
    Extrai texto de uma página do PDF.
    
    Args:
        page: Página do PyMuPDF
        
    Returns:
        Tupla (texto, usou_ocr)
    """
    # Tenta extração nativa primeiro
    text = page.get_text("text")
    
    # Verifica se há texto suficiente
    if text and len(text.strip()) > 50:
        return text.strip(), False
    
    # Texto insuficiente - precisa de OCR
    return "", True


def apply_ocr_to_page(page: fitz.Page, dpi: int = 300) -> str:
    """
    Aplica OCR a uma página do PDF.
    
    Args:
        page: Página do PyMuPDF
        dpi: Resolução para renderização
        
    Returns:
        Texto extraído via OCR
        
    Raises:
        OCRError: Se o OCR falhar
    """
    try:
        # Renderiza página como imagem
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        pix = page.get_pixmap(matrix=mat)
        
        # Converte para PIL Image
        img_data = pix.tobytes("png")
        image = Image.open(io.BytesIO(img_data))
        
        # Aplica OCR
        # Usa português como idioma padrão
        text = pytesseract.image_to_string(
            image,
            lang='por',
            config='--psm 1',  # Automatic page segmentation with OSD
        )
        
        return text.strip()
        
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract não instalado! Execute: apt install tesseract-ocr tesseract-ocr-por")
        raise OCRError("Tesseract não encontrado")
    except Exception as e:
        logger.error(f"Erro no OCR: {e}")
        raise OCRError(f"Falha no OCR: {e}")


def calculate_confidence(text: str, ocr_used: bool) -> float:
    """
    Calcula confiança da extração.
    
    Args:
        text: Texto extraído
        ocr_used: Se OCR foi usado
        
    Returns:
        Score de confiança (0.0 a 1.0)
    """
    if not text:
        return 0.0
    
    # Base de confiança
    confidence = 1.0 if not ocr_used else 0.7
    
    # Penaliza textos muito curtos
    if len(text) < 100:
        confidence *= 0.5
    elif len(text) < 500:
        confidence *= 0.8
    
    # Penaliza alta proporção de caracteres especiais
    special_chars = sum(1 for c in text if not c.isalnum() and c not in ' \n\t.,;:!?()-')
    if len(text) > 0:
        special_ratio = special_chars / len(text)
        if special_ratio > 0.3:
            confidence *= 0.7
    
    return min(1.0, max(0.0, confidence))


def extract_all_pages(pdf_path: Path, skip_first: bool = True) -> List[PageContent]:
    """
    Extrai texto de todas as páginas do PDF.
    
    Args:
        pdf_path: Caminho do PDF
        skip_first: Se True, ignora a primeira página (capa)
        
    Returns:
        Lista de PageContent com texto extraído
    """
    pages = []
    
    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        
        logger.info(f"PDF tem {total_pages} páginas")
        
        start_page = 1 if skip_first else 0
        
        for page_num in range(start_page, total_pages):
            logger.debug(f"Processando página {page_num + 1}/{total_pages}")
            
            page = doc[page_num]
            
            # Extrai texto
            text, needs_ocr = extract_text_from_page(page)
            
            if needs_ocr:
                logger.info(f"Página {page_num + 1}: Aplicando OCR...")
                try:
                    text = apply_ocr_to_page(page)
                except OCRError as e:
                    logger.warning(f"OCR falhou para página {page_num + 1}: {e}")
                    text = ""
            
            # Calcula confiança
            confidence = calculate_confidence(text, needs_ocr)
            
            pages.append(PageContent(
                page=page_num + 1,
                text=text,
                ocr_used=needs_ocr,
                confidence=confidence,
            ))
            
            logger.debug(
                f"Página {page_num + 1}: {len(text)} chars, "
                f"OCR={needs_ocr}, confiança={confidence:.2f}"
            )
        
        doc.close()
        
        logger.info(f"Extração concluída: {len(pages)} páginas processadas")
        return pages
        
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        raise ProcessingError(f"Falha ao processar PDF: {e}")


def save_verification_report(
    pages: List[PageContent],
    output_dir: Path,
) -> Path:
    """
    Salva relatório de verificação página a página.
    
    Args:
        pages: Lista de páginas processadas
        output_dir: Diretório de saída
        
    Returns:
        Path do arquivo de verificação
    """
    filename = get_output_filename("verification", "txt")
    filepath = output_dir / filename
    
    lines = [
        "=" * 60,
        "RELATÓRIO DE VERIFICAÇÃO - EXTRAÇÃO DE TEXTO",
        f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
    ]
    
    for page in pages:
        lines.extend([
            f"PÁGINA {page.page}",
            "-" * 40,
            f"  OCR usado: {'Sim' if page.ocr_used else 'Não'}",
            f"  Confiança: {page.confidence:.2%}",
            f"  Tamanho: {len(page.text)} caracteres",
            f"  Preview: {page.text[:200]}..." if len(page.text) > 200 else f"  Texto: {page.text}",
            "",
        ])
    
    # Estatísticas
    total_ocr = sum(1 for p in pages if p.ocr_used)
    avg_confidence = sum(p.confidence for p in pages) / len(pages) if pages else 0
    
    lines.extend([
        "=" * 60,
        "ESTATÍSTICAS",
        "=" * 60,
        f"Total de páginas: {len(pages)}",
        f"Páginas com OCR: {total_ocr} ({100*total_ocr/len(pages):.1f}%)" if pages else "N/A",
        f"Confiança média: {avg_confidence:.2%}",
        "",
    ])
    
    filepath.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Relatório de verificação salvo: {filepath}")
    
    return filepath


def save_clipage_files(
    result: Dict[str, Any],
    pages: List[PageContent],
    output_dir: Path,
) -> tuple[Path, Path]:
    """
    Salva arquivos de clipagem (TXT e JSON).
    
    Args:
        result: Resultado do LLM
        pages: Páginas processadas
        output_dir: Diretório de saída
        
    Returns:
        Tupla (path_txt, path_json)
    """
    # Arquivo TXT
    txt_filename = get_output_filename("clipagem", "txt")
    txt_path = output_dir / txt_filename
    
    txt_content = [
        "=" * 60,
        f"CLIPAGEM DO DIÁRIO - {datetime.now().strftime('%d/%m/%Y')}",
        "=" * 60,
        "",
        result["summary_text"],
        "",
        "=" * 60,
        f"Gerado automaticamente pelo Jornal-Agent",
        f"Total de itens: {result['metadata'].get('total_items', 0)}",
        "=" * 60,
    ]
    
    txt_path.write_text("\n".join(txt_content), encoding="utf-8")
    logger.info(f"Clipagem TXT salva: {txt_path}")
    
    # Arquivo JSON
    json_filename = get_output_filename("clipagem", "json")
    json_path = output_dir / json_filename
    
    json_data = {
        "date": datetime.now().isoformat(),
        "items": result["items"],
        "metadata": result["metadata"],
        "pages": [
            {
                "page": p.page,
                "ocr_used": p.ocr_used,
                "confidence": p.confidence,
                "text_length": len(p.text),
            }
            for p in pages
        ],
    }
    
    json_path.write_text(
        json.dumps(json_data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"Clipagem JSON salva: {json_path}")
    
    return txt_path, json_path


def process_pdf(pdf_path: Path, config: Config) -> Dict[str, Any]:
    """
    Processa o PDF e gera clipagem completa.
    
    Esta função:
    1. Extrai texto de todas as páginas (exceto capa)
    2. Aplica OCR quando necessário
    3. Envia ao LLM para geração de clipagem
    4. Salva arquivos de saída
    
    Args:
        pdf_path: Caminho do PDF a processar
        config: Configurações do aplicativo
        
    Returns:
        Dicionário com:
        - summary_text: Texto da clipagem
        - total_pages: Número de páginas processadas
        - total_items: Número de itens na clipagem
        - txt_file: Path do arquivo TXT
        - json_file: Path do arquivo JSON
        - verification_file: Path do relatório de verificação
        
    Raises:
        ProcessingError: Se o processamento falhar
    """
    logger.info(f"Iniciando processamento: {pdf_path}")
    
    if not pdf_path.exists():
        raise ProcessingError(f"PDF não encontrado: {pdf_path}")
    
    # Garante diretório de saída
    config.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Modo dry-run: retorna resultado simulado
    if config.dry_run:
        logger.warning("Modo DRY-RUN: Retornando processamento simulado")
        
        dummy_pages = [
            PageContent(page=2, text="Notícia de economia simulada", ocr_used=False, confidence=0.95),
            PageContent(page=3, text="Notícia de política simulada", ocr_used=False, confidence=0.90),
        ]
        
        llm_result = summarize_pages(dummy_pages, config)
        txt_file, json_file = save_clipage_files(llm_result, dummy_pages, config.output_dir)
        verification_file = save_verification_report(dummy_pages, config.output_dir)
        
        return {
            "summary_text": llm_result["summary_text"],
            "total_pages": 2,
            "total_items": len(llm_result["items"]),
            "txt_file": str(txt_file),
            "json_file": str(json_file),
            "verification_file": str(verification_file),
            "items": llm_result["items"],
            "metadata": {"dry_run": True},
        }
    
    try:
        # Passo 1: Extração de texto
        logger.info("Passo 1: Extraindo texto das páginas...")
        pages = extract_all_pages(pdf_path, skip_first=True)
        
        if not pages:
            raise ProcessingError("Nenhuma página extraída do PDF")
        
        # Passo 2: Salva relatório de verificação
        logger.info("Passo 2: Gerando relatório de verificação...")
        verification_file = save_verification_report(pages, config.output_dir)
        
        # Passo 3: Envia ao LLM
        logger.info("Passo 3: Gerando clipagem via LLM...")
        llm_result = summarize_pages(pages, config)
        
        # Passo 4: Salva arquivos de saída
        logger.info("Passo 4: Salvando arquivos de saída...")
        txt_file, json_file = save_clipage_files(llm_result, pages, config.output_dir)
        
        result = {
            "summary_text": llm_result["summary_text"],
            "total_pages": len(pages),
            "total_items": len(llm_result["items"]),
            "txt_file": str(txt_file),
            "json_file": str(json_file),
            "verification_file": str(verification_file),
            "items": llm_result["items"],
            "metadata": llm_result["metadata"],
        }
        
        logger.success("Processamento concluído com sucesso!")
        return result
        
    except LLMError as e:
        logger.error(f"Erro no LLM: {e}")
        raise ProcessingError(f"Falha na geração de clipagem: {e}")
    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        raise ProcessingError(f"Falha no processamento: {e}")


if __name__ == "__main__":
    # Teste do módulo
    from src.config import load_config
    
    config = load_config(dry_run=True)
    
    # Cria PDF de teste
    test_pdf = config.data_dir / "test.pdf"
    if not test_pdf.exists():
        print(f"Crie um PDF de teste em: {test_pdf}")
    else:
        result = process_pdf(test_pdf, config)
        print("Resultado:")
        print(f"  Páginas: {result['total_pages']}")
        print(f"  Itens: {result['total_items']}")
        print(f"  TXT: {result['txt_file']}")
