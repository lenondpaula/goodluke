"""
Jornal-Agent - Cliente WhatsApp.

Este módulo implementa o envio de mensagens e arquivos
via WhatsApp Cloud API.

IMPORTANTE: Configure os seguintes secrets:
- WHATSAPP_TOKEN: Token de acesso permanente do Meta
- WHATSAPP_PHONE_ID: ID do número de telefone do WhatsApp Business

Documentação da API:
https://developers.facebook.com/docs/whatsapp/cloud-api/

Para obter as credenciais:
1. Crie uma conta no Meta for Developers
2. Configure um app com WhatsApp Business
3. Obtenha o token de acesso e Phone ID
"""

import time
import json
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional
import base64

import requests
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config


class WhatsAppError(Exception):
    """Erro genérico do WhatsApp."""
    pass


class WhatsAppRateLimitError(WhatsAppError):
    """Rate limit atingido."""
    pass


class WhatsAppAuthError(WhatsAppError):
    """Erro de autenticação."""
    pass


class WhatsAppMediaError(WhatsAppError):
    """Erro no upload de mídia."""
    pass


# URLs da API
WHATSAPP_API_BASE = "https://graph.facebook.com/v18.0"


def get_headers(token: str) -> Dict[str, str]:
    """
    Retorna headers para requisições à API.
    
    Args:
        token: Token de acesso
        
    Returns:
        Headers para requisição
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def check_response(response: requests.Response) -> Dict[str, Any]:
    """
    Verifica resposta da API e trata erros.
    
    Args:
        response: Resposta da requisição
        
    Returns:
        JSON da resposta
        
    Raises:
        WhatsAppError: Se houver erro
    """
    try:
        data = response.json()
    except json.JSONDecodeError:
        raise WhatsAppError(f"Resposta inválida: {response.text}")
    
    if response.status_code == 429:
        raise WhatsAppRateLimitError("Rate limit atingido")
    
    if response.status_code == 401:
        raise WhatsAppAuthError("Token de acesso inválido ou expirado")
    
    if response.status_code >= 400:
        error = data.get("error", {})
        message = error.get("message", "Erro desconhecido")
        code = error.get("code", response.status_code)
        raise WhatsAppError(f"Erro {code}: {message}")
    
    return data


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(WhatsAppRateLimitError),
)
def upload_media(
    pdf_path: Path,
    phone_id: str,
    token: str,
) -> str:
    """
    Faz upload de mídia para o WhatsApp.
    
    Args:
        pdf_path: Caminho do arquivo PDF
        phone_id: ID do telefone WhatsApp Business
        token: Token de acesso
        
    Returns:
        Media ID do arquivo uploadado
        
    Raises:
        WhatsAppMediaError: Se o upload falhar
    """
    url = f"{WHATSAPP_API_BASE}/{phone_id}/media"
    
    # Detecta tipo MIME
    mime_type, _ = mimetypes.guess_type(str(pdf_path))
    if not mime_type:
        mime_type = "application/pdf"
    
    logger.info(f"Fazendo upload de mídia: {pdf_path.name}")
    
    try:
        with open(pdf_path, "rb") as f:
            files = {
                "file": (pdf_path.name, f, mime_type),
            }
            data = {
                "messaging_product": "whatsapp",
                "type": mime_type,
            }
            
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {token}"},
                files=files,
                data=data,
                timeout=120,  # Upload pode demorar
            )
        
        result = check_response(response)
        media_id = result.get("id")
        
        if not media_id:
            raise WhatsAppMediaError("Media ID não retornado")
        
        logger.info(f"Upload concluído. Media ID: {media_id}")
        return media_id
        
    except requests.RequestException as e:
        raise WhatsAppMediaError(f"Erro no upload: {e}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(WhatsAppRateLimitError),
)
def send_document(
    to_phone: str,
    media_id: str,
    caption: str,
    phone_id: str,
    token: str,
) -> Dict[str, Any]:
    """
    Envia documento via WhatsApp.
    
    Args:
        to_phone: Número do destinatário (formato: 5511999999999)
        media_id: ID da mídia no WhatsApp
        caption: Legenda do documento
        phone_id: ID do telefone remetente
        token: Token de acesso
        
    Returns:
        Resposta da API
    """
    url = f"{WHATSAPP_API_BASE}/{phone_id}/messages"
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "document",
        "document": {
            "id": media_id,
            "caption": caption[:1024],  # Limite de caracteres
            "filename": f"diario-{time.strftime('%Y%m%d')}.pdf",
        },
    }
    
    logger.info(f"Enviando documento para: {to_phone[:5]}***")
    
    response = requests.post(
        url,
        headers=get_headers(token),
        json=payload,
        timeout=30,
    )
    
    result = check_response(response)
    logger.info(f"Documento enviado. Message ID: {result.get('messages', [{}])[0].get('id')}")
    
    return result


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(WhatsAppRateLimitError),
)
def send_text_message(
    to_phone: str,
    text: str,
    phone_id: str,
    token: str,
) -> Dict[str, Any]:
    """
    Envia mensagem de texto via WhatsApp.
    
    Args:
        to_phone: Número do destinatário
        text: Texto da mensagem
        phone_id: ID do telefone remetente
        token: Token de acesso
        
    Returns:
        Resposta da API
    """
    url = f"{WHATSAPP_API_BASE}/{phone_id}/messages"
    
    # WhatsApp tem limite de 4096 caracteres por mensagem
    # Trunca se necessário
    if len(text) > 4000:
        text = text[:3997] + "..."
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": text,
        },
    }
    
    logger.info(f"Enviando mensagem de texto para: {to_phone[:5]}***")
    
    response = requests.post(
        url,
        headers=get_headers(token),
        json=payload,
        timeout=30,
    )
    
    result = check_response(response)
    logger.info(f"Mensagem enviada. Message ID: {result.get('messages', [{}])[0].get('id')}")
    
    return result


def send_media(
    to_phone: str,
    pdf_path: Path,
    message_text: str,
    config: Config,
) -> Dict[str, Any]:
    """
    Envia PDF e mensagem de texto via WhatsApp.
    
    Esta função:
    1. Faz upload do PDF
    2. Envia o documento com caption
    3. Envia mensagem de texto com resumo completo
    
    Args:
        to_phone: Número do destinatário
        pdf_path: Caminho do PDF
        message_text: Texto da mensagem (clipagem)
        config: Configurações do aplicativo
        
    Returns:
        Dicionário com status e IDs das mensagens
        
    Raises:
        WhatsAppError: Se o envio falhar
    """
    if not to_phone:
        raise WhatsAppError("Número do destinatário não configurado (WHATSAPP_RECIPIENT)")
    
    # Remove caracteres não numéricos
    to_phone = "".join(filter(str.isdigit, to_phone))
    
    if not to_phone:
        raise WhatsAppError("Número do destinatário inválido")
    
    logger.info(f"Iniciando envio via WhatsApp...")
    logger.debug(f"Destinatário: {to_phone[:5]}***")
    logger.debug(f"PDF: {pdf_path}")
    
    result = {
        "success": False,
        "document_message_id": None,
        "text_message_id": None,
        "media_id": None,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    
    try:
        # Passo 1: Upload do PDF
        media_id = upload_media(
            pdf_path=pdf_path,
            phone_id=config.whatsapp_phone_id,
            token=config.whatsapp_token,
        )
        result["media_id"] = media_id
        
        # Passo 2: Envia documento
        doc_result = send_document(
            to_phone=to_phone,
            media_id=media_id,
            caption=f"📰 Edição de {time.strftime('%d/%m/%Y')}",
            phone_id=config.whatsapp_phone_id,
            token=config.whatsapp_token,
        )
        result["document_message_id"] = doc_result.get("messages", [{}])[0].get("id")
        
        # Pequena pausa entre mensagens
        time.sleep(1)
        
        # Passo 3: Envia texto com clipagem
        text_result = send_text_message(
            to_phone=to_phone,
            text=message_text,
            phone_id=config.whatsapp_phone_id,
            token=config.whatsapp_token,
        )
        result["text_message_id"] = text_result.get("messages", [{}])[0].get("id")
        
        result["success"] = True
        logger.success("Envio via WhatsApp concluído com sucesso!")
        
        return result
        
    except WhatsAppAuthError as e:
        logger.error(f"Erro de autenticação: {e}")
        raise
    except WhatsAppError as e:
        logger.error(f"Erro no WhatsApp: {e}")
        raise
    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        raise WhatsAppError(f"Falha no envio: {e}")


if __name__ == "__main__":
    # Teste do módulo (requer configuração)
    from src.config import load_config
    
    config = load_config(dry_run=True)
    
    print("Para testar o envio WhatsApp, configure:")
    print("  - WHATSAPP_TOKEN")
    print("  - WHATSAPP_PHONE_ID")
    print("  - WHATSAPP_RECIPIENT")
    print("")
    print("Documentação: https://developers.facebook.com/docs/whatsapp/cloud-api/")
