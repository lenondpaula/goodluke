"""
Jornal-Agent - Cliente LLM.

Este módulo implementa a integração com APIs de LLM para
geração de resumos e clipagem do conteúdo do jornal.

Suporta:
- OpenAI (GPT-4, GPT-3.5)
- DeepSeek
- Qualquer API compatível com OpenAI
"""

import json
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from openai import OpenAI
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config


@dataclass
class PageContent:
    """Conteúdo extraído de uma página."""
    page: int
    text: str
    ocr_used: bool
    confidence: float


@dataclass
class ClipageItem:
    """Item da clipagem."""
    page: int
    subject: str
    summary: str


class LLMError(Exception):
    """Erro na comunicação com o LLM."""
    pass


class RateLimitError(Exception):
    """Rate limit atingido."""
    pass


# Prompt padrão DeepSeek para clipagem
DEFAULT_PROMPT_TEMPLATE = """Você é um assistente especializado em análise de jornais e geração de clipagens.

Analise o conteúdo das páginas do jornal fornecidas e gere uma clipagem seguindo estas regras:

**CRITÉRIOS DE SELEÇÃO:**
- Foque em notícias relevantes sobre política, economia, negócios, tecnologia e assuntos locais importantes
- IGNORE anúncios, classificados e propagandas
- IGNORE a capa (página 1) pois já é um resumo
- NÃO inclua obituários, horóscopo ou entretenimento leve

**FORMATO DE SAÍDA:**
Para cada item relevante, use exatamente este formato (uma linha por item):

Página X | **Assunto/Tema** | Resumo breve (máximo 150 caracteres)

- Use asteriscos para negrito no assunto/tema: **Exemplo**
- Deixe uma linha em branco entre cada item
- Limite cada resumo a NO MÁXIMO 150 caracteres
- Ordene por página

**EXEMPLO DE SAÍDA:**
Página 2 | **Economia** | Banco Central mantém taxa Selic em 10,5% e sinaliza cautela com inflação.

Página 3 | **Política** | Senado aprova projeto de lei sobre reforma tributária com emendas.

Página 5 | **Tecnologia** | Startup brasileira recebe aporte de R$ 50 milhões para expansão.

---

**CONTEÚDO DO JORNAL PARA ANALISAR:**

{content}

---

Gere a clipagem seguindo rigorosamente o formato especificado:"""


def create_client(config: Config) -> OpenAI:
    """
    Cria cliente OpenAI/compatível.
    
    Args:
        config: Configurações do aplicativo
        
    Returns:
        Cliente OpenAI configurado
    """
    kwargs = {
        "api_key": config.llm_api_key,
    }
    
    if config.llm_base_url:
        kwargs["base_url"] = config.llm_base_url
        logger.debug(f"Usando base URL customizada: {config.llm_base_url}")
    
    return OpenAI(**kwargs)


def chunk_pages(pages: List[PageContent], max_chars: int = 30000) -> List[List[PageContent]]:
    """
    Divide páginas em chunks para evitar limite de tokens.
    
    Args:
        pages: Lista de páginas
        max_chars: Máximo de caracteres por chunk
        
    Returns:
        Lista de chunks (cada chunk é uma lista de páginas)
    """
    chunks = []
    current_chunk = []
    current_size = 0
    
    for page in pages:
        page_size = len(page.text)
        
        if current_size + page_size > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0
        
        current_chunk.append(page)
        current_size += page_size
    
    if current_chunk:
        chunks.append(current_chunk)
    
    logger.info(f"Páginas divididas em {len(chunks)} chunk(s)")
    return chunks


def format_pages_for_prompt(pages: List[PageContent]) -> str:
    """
    Formata páginas para inclusão no prompt.
    
    Args:
        pages: Lista de páginas
        
    Returns:
        Texto formatado para o prompt
    """
    formatted = []
    
    for page in pages:
        ocr_note = " [OCR]" if page.ocr_used else ""
        formatted.append(f"--- PÁGINA {page.page}{ocr_note} ---\n{page.text}\n")
    
    return "\n".join(formatted)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(RateLimitError),
)
def call_llm(
    client: OpenAI,
    model: str,
    prompt: str,
    max_tokens: int = 4000,
) -> str:
    """
    Faz chamada ao LLM com retry automático.
    
    Args:
        client: Cliente OpenAI
        model: Nome do modelo
        prompt: Prompt completo
        max_tokens: Limite de tokens na resposta
        
    Returns:
        Resposta do LLM
        
    Raises:
        LLMError: Se a chamada falhar
        RateLimitError: Se rate limit for atingido
    """
    try:
        logger.debug(f"Chamando LLM ({model})...")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente especializado em análise de jornais.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=max_tokens,
            temperature=0.3,  # Baixa temperatura para respostas consistentes
        )
        
        result = response.choices[0].message.content
        logger.debug(f"Resposta recebida: {len(result)} caracteres")
        
        return result
        
    except Exception as e:
        error_str = str(e).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            logger.warning("Rate limit atingido, aguardando...")
            raise RateLimitError(str(e))
        
        logger.error(f"Erro na chamada LLM: {e}")
        raise LLMError(f"Falha na comunicação com LLM: {e}")


def parse_clipage_response(response: str) -> List[ClipageItem]:
    """
    Faz parsing da resposta do LLM para extrair itens de clipagem.
    
    Args:
        response: Resposta do LLM
        
    Returns:
        Lista de itens de clipagem
    """
    items = []
    lines = response.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('---'):
            continue
        
        # Tenta fazer parsing do formato: "Página X | **Assunto** | Resumo"
        if '|' in line and 'Página' in line:
            parts = line.split('|')
            if len(parts) >= 3:
                try:
                    # Extrai número da página
                    page_part = parts[0].strip()
                    page_num = int(''.join(filter(str.isdigit, page_part)) or '0')
                    
                    # Extrai assunto
                    subject = parts[1].strip()
                    
                    # Extrai resumo
                    summary = '|'.join(parts[2:]).strip()
                    
                    # Limita resumo a 150 caracteres
                    if len(summary) > 150:
                        summary = summary[:147] + "..."
                    
                    items.append(ClipageItem(
                        page=page_num,
                        subject=subject,
                        summary=summary,
                    ))
                    
                except (ValueError, IndexError) as e:
                    logger.debug(f"Erro ao parsear linha: {line} - {e}")
                    continue
    
    logger.info(f"Extraídos {len(items)} itens da clipagem")
    return items


def summarize_pages(
    pages: List[PageContent],
    config: Config,
    prompt_template: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Processa páginas e gera clipagem via LLM.
    
    Args:
        pages: Lista de páginas com conteúdo extraído
        config: Configurações do aplicativo
        prompt_template: Template de prompt customizado (opcional)
        
    Returns:
        Dicionário com:
        - summary_text: Texto formatado da clipagem
        - items: Lista de itens estruturados
        - metadata: Metadados do processamento
    """
    if not pages:
        logger.warning("Nenhuma página para processar")
        return {
            "summary_text": "Nenhum conteúdo para processar.",
            "items": [],
            "metadata": {"error": "Sem páginas"},
        }
    
    template = prompt_template or DEFAULT_PROMPT_TEMPLATE
    
    # Modo dry-run: retorna resposta simulada
    if config.dry_run:
        logger.warning("Modo DRY-RUN: Retornando clipagem simulada")
        return {
            "summary_text": (
                "Página 2 | **Economia** | [SIMULADO] Exemplo de notícia econômica.\n\n"
                "Página 3 | **Política** | [SIMULADO] Exemplo de notícia política.\n\n"
                "Página 5 | **Local** | [SIMULADO] Exemplo de notícia local."
            ),
            "items": [
                {"page": 2, "subject": "**Economia**", "summary": "[SIMULADO] Exemplo"},
                {"page": 3, "subject": "**Política**", "summary": "[SIMULADO] Exemplo"},
            ],
            "metadata": {"dry_run": True},
        }
    
    # Cria cliente LLM
    client = create_client(config)
    
    # Divide em chunks se necessário
    chunks = chunk_pages(pages)
    
    all_items = []
    all_responses = []
    
    for i, chunk in enumerate(chunks):
        logger.info(f"Processando chunk {i+1}/{len(chunks)}...")
        
        # Formata páginas para o prompt
        content = format_pages_for_prompt(chunk)
        prompt = template.format(content=content)
        
        # Chama LLM
        response = call_llm(
            client=client,
            model=config.llm_model,
            prompt=prompt,
        )
        
        all_responses.append(response)
        
        # Extrai itens
        items = parse_clipage_response(response)
        all_items.extend(items)
        
        # Pequena pausa entre chunks para evitar rate limit
        if i < len(chunks) - 1:
            time.sleep(1)
    
    # Ordena por página
    all_items.sort(key=lambda x: x.page)
    
    # Formata texto final
    summary_lines = []
    for item in all_items:
        summary_lines.append(f"Página {item.page} | {item.subject} | {item.summary}")
    
    summary_text = "\n\n".join(summary_lines)
    
    return {
        "summary_text": summary_text,
        "items": [
            {"page": item.page, "subject": item.subject, "summary": item.summary}
            for item in all_items
        ],
        "metadata": {
            "total_pages": len(pages),
            "total_items": len(all_items),
            "chunks_processed": len(chunks),
            "model": config.llm_model,
        },
    }


if __name__ == "__main__":
    # Teste do módulo
    from src.config import load_config
    
    config = load_config(dry_run=True)
    
    # Simula páginas
    pages = [
        PageContent(page=1, text="Capa do jornal...", ocr_used=False, confidence=1.0),
        PageContent(page=2, text="Notícia de economia...", ocr_used=False, confidence=0.95),
    ]
    
    result = summarize_pages(pages, config)
    print("Resultado:")
    print(result["summary_text"])
