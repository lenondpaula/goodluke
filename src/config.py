"""
Configuração do Jornal-Agent.

Este módulo carrega e valida todas as variáveis de ambiente necessárias.
IMPORTANTE: Nunca hardcode credenciais. Use variáveis de ambiente ou GitHub Secrets.

Variáveis de ambiente necessárias (adicionar em GitHub Secrets):
- JORNAL_USER: Usuário para login no jornal
- JORNAL_PASS: Senha para login no jornal
- LLM_API_KEY: Chave da API do LLM (OpenAI, DeepSeek, etc.)
- WHATSAPP_TOKEN: Token de acesso da WhatsApp Cloud API
- WHATSAPP_PHONE_ID: ID do número de telefone do WhatsApp Business

Variáveis opcionais (para fallback por e-mail):
- SMTP_HOST: Servidor SMTP
- SMTP_PORT: Porta do servidor SMTP
- SMTP_USER: Usuário SMTP
- SMTP_PASS: Senha SMTP
- EMAIL_FROM: E-mail remetente
- EMAIL_TO: E-mail destinatário
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from loguru import logger

# Tenta carregar .env para desenvolvimento local
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class Config:
    """Configurações do aplicativo."""
    
    # Credenciais do Jornal
    jornal_user: str
    jornal_pass: str
    jornal_login_url: str
    jornal_pdf_url: str
    
    # LLM
    llm_api_key: str
    llm_model: str
    llm_base_url: Optional[str]
    
    # WhatsApp
    whatsapp_token: str
    whatsapp_phone_id: str
    whatsapp_recipient: str
    
    # SMTP (opcional)
    smtp_host: Optional[str]
    smtp_port: Optional[int]
    smtp_user: Optional[str]
    smtp_pass: Optional[str]
    email_from: Optional[str]
    email_to: Optional[str]
    
    # Diretórios
    data_dir: Path
    output_dir: Path
    
    # Configurações gerais
    timeout: int
    max_retries: int
    dry_run: bool


class ConfigError(Exception):
    """Erro de configuração - variável de ambiente ausente ou inválida."""
    pass


def get_required_env(name: str) -> str:
    """
    Obtém uma variável de ambiente obrigatória.
    
    Args:
        name: Nome da variável de ambiente
        
    Returns:
        Valor da variável
        
    Raises:
        ConfigError: Se a variável não estiver definida
    """
    value = os.environ.get(name)
    if not value:
        raise ConfigError(
            f"Variável de ambiente obrigatória '{name}' não está definida. "
            f"Adicione-a em GitHub Secrets ou no arquivo .env local."
        )
    return value


def get_optional_env(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtém uma variável de ambiente opcional.
    
    Args:
        name: Nome da variável de ambiente
        default: Valor padrão se não estiver definida
        
    Returns:
        Valor da variável ou o padrão
    """
    return os.environ.get(name, default)


def load_config(dry_run: bool = False) -> Config:
    """
    Carrega e valida todas as configurações.
    
    Args:
        dry_run: Se True, algumas validações são relaxadas para testes
        
    Returns:
        Objeto Config com todas as configurações
        
    Raises:
        ConfigError: Se alguma configuração obrigatória estiver faltando
    """
    logger.info("Carregando configurações...")
    
    # Diretórios base
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    output_dir = base_dir / "output"
    
    # Criar diretórios se não existirem
    data_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Em modo dry_run, aceita valores vazios para credenciais
        if dry_run:
            jornal_user = get_optional_env("JORNAL_USER", "test_user")
            jornal_pass = get_optional_env("JORNAL_PASS", "test_pass")
            llm_api_key = get_optional_env("LLM_API_KEY", "test_key")
            whatsapp_token = get_optional_env("WHATSAPP_TOKEN", "test_token")
            whatsapp_phone_id = get_optional_env("WHATSAPP_PHONE_ID", "test_phone_id")
        else:
            jornal_user = get_required_env("JORNAL_USER")
            jornal_pass = get_required_env("JORNAL_PASS")
            llm_api_key = get_required_env("LLM_API_KEY")
            whatsapp_token = get_required_env("WHATSAPP_TOKEN")
            whatsapp_phone_id = get_required_env("WHATSAPP_PHONE_ID")
        
        config = Config(
            # Jornal
            jornal_user=jornal_user,
            jornal_pass=jornal_pass,
            jornal_login_url=get_optional_env(
                "JORNAL_LOGIN_URL", 
                "https://exemplo-jornal.com.br/login"
            ),
            jornal_pdf_url=get_optional_env(
                "JORNAL_PDF_URL",
                "https://exemplo-jornal.com.br/assinante/edicao"
            ),
            
            # LLM
            llm_api_key=llm_api_key,
            llm_model=get_optional_env("LLM_MODEL", "gpt-4o-mini"),
            llm_base_url=get_optional_env("LLM_BASE_URL"),
            
            # WhatsApp
            whatsapp_token=whatsapp_token,
            whatsapp_phone_id=whatsapp_phone_id,
            whatsapp_recipient=get_optional_env("WHATSAPP_RECIPIENT", ""),
            
            # SMTP (opcional)
            smtp_host=get_optional_env("SMTP_HOST"),
            smtp_port=int(get_optional_env("SMTP_PORT", "587")),
            smtp_user=get_optional_env("SMTP_USER"),
            smtp_pass=get_optional_env("SMTP_PASS"),
            email_from=get_optional_env("EMAIL_FROM"),
            email_to=get_optional_env("EMAIL_TO"),
            
            # Diretórios
            data_dir=data_dir,
            output_dir=output_dir,
            
            # Configurações gerais
            timeout=int(get_optional_env("TIMEOUT", "60")),
            max_retries=int(get_optional_env("MAX_RETRIES", "3")),
            dry_run=dry_run,
        )
        
        logger.info("Configurações carregadas com sucesso")
        logger.debug(f"Data dir: {config.data_dir}")
        logger.debug(f"Output dir: {config.output_dir}")
        logger.debug(f"Dry run: {config.dry_run}")
        
        return config
        
    except ConfigError as e:
        logger.error(f"Erro de configuração: {e}")
        raise


def validate_smtp_config(config: Config) -> bool:
    """
    Valida se a configuração SMTP está completa para fallback por e-mail.
    
    Args:
        config: Objeto de configuração
        
    Returns:
        True se SMTP está configurado, False caso contrário
    """
    required_smtp = [
        config.smtp_host,
        config.smtp_user,
        config.smtp_pass,
        config.email_from,
        config.email_to,
    ]
    return all(required_smtp)


# Lista de variáveis de ambiente para documentação
REQUIRED_SECRETS = [
    ("JORNAL_USER", "Usuário para login no jornal"),
    ("JORNAL_PASS", "Senha para login no jornal"),
    ("LLM_API_KEY", "Chave da API do LLM"),
    ("WHATSAPP_TOKEN", "Token de acesso da WhatsApp Cloud API"),
    ("WHATSAPP_PHONE_ID", "ID do número de telefone do WhatsApp Business"),
]

OPTIONAL_SECRETS = [
    ("JORNAL_LOGIN_URL", "URL de login do jornal"),
    ("JORNAL_PDF_URL", "URL da página do PDF"),
    ("LLM_MODEL", "Modelo do LLM a usar (padrão: gpt-4o-mini)"),
    ("LLM_BASE_URL", "URL base da API do LLM (para APIs compatíveis)"),
    ("WHATSAPP_RECIPIENT", "Número do destinatário WhatsApp"),
    ("SMTP_HOST", "Servidor SMTP para fallback"),
    ("SMTP_PORT", "Porta SMTP (padrão: 587)"),
    ("SMTP_USER", "Usuário SMTP"),
    ("SMTP_PASS", "Senha SMTP"),
    ("EMAIL_FROM", "E-mail remetente"),
    ("EMAIL_TO", "E-mail destinatário"),
    ("TIMEOUT", "Timeout em segundos (padrão: 60)"),
    ("MAX_RETRIES", "Número máximo de retentativas (padrão: 3)"),
]


if __name__ == "__main__":
    # Teste de carregamento de configuração
    try:
        config = load_config(dry_run=True)
        print("✓ Configuração carregada com sucesso!")
        print(f"  Data dir: {config.data_dir}")
        print(f"  Output dir: {config.output_dir}")
    except ConfigError as e:
        print(f"✗ Erro: {e}")
        sys.exit(1)
