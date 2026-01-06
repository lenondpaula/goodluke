"""
Jornal-Agent - Módulo de Notificações.

Este módulo implementa:
- Fallback por e-mail quando WhatsApp falha
- Atualização de status da execução
- Notificações de erro
"""

import json
import smtplib
import ssl
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Dict, Any, Optional

from loguru import logger

from src.config import Config, validate_smtp_config


class EmailError(Exception):
    """Erro no envio de e-mail."""
    pass


def send_email_fallback(
    subject: str,
    body: str,
    attachment_path: Optional[Path],
    config: Config,
) -> bool:
    """
    Envia e-mail como fallback quando WhatsApp falha.
    
    Args:
        subject: Assunto do e-mail
        body: Corpo do e-mail
        attachment_path: Caminho do arquivo anexo (opcional)
        config: Configurações do aplicativo
        
    Returns:
        True se enviado com sucesso
        
    Raises:
        EmailError: Se o envio falhar
    """
    if not validate_smtp_config(config):
        raise EmailError(
            "Configuração SMTP incompleta. Defina: "
            "SMTP_HOST, SMTP_USER, SMTP_PASS, EMAIL_FROM, EMAIL_TO"
        )
    
    logger.info(f"Enviando e-mail de fallback para: {config.email_to}")
    
    try:
        # Cria mensagem
        msg = MIMEMultipart()
        msg["From"] = config.email_from
        msg["To"] = config.email_to
        msg["Subject"] = subject
        
        # Corpo do e-mail
        email_body = f"""
Olá,

Segue a clipagem do jornal gerada automaticamente.

---
{body}
---

Este e-mail foi enviado automaticamente pelo Jornal-Agent.
O envio via WhatsApp falhou, então este é um fallback por e-mail.

Data: {datetime.now().strftime('%d/%m/%Y às %H:%M')}
"""
        msg.attach(MIMEText(email_body, "plain", "utf-8"))
        
        # Anexo
        if attachment_path and attachment_path.exists():
            with open(attachment_path, "rb") as f:
                attachment = MIMEApplication(f.read(), _subtype="pdf")
                attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=attachment_path.name,
                )
                msg.attach(attachment)
            logger.debug(f"Anexo adicionado: {attachment_path.name}")
        
        # Conexão SMTP
        context = ssl.create_default_context()
        
        with smtplib.SMTP(config.smtp_host, config.smtp_port) as server:
            server.starttls(context=context)
            server.login(config.smtp_user, config.smtp_pass)
            server.send_message(msg)
        
        logger.success("E-mail enviado com sucesso!")
        return True
        
    except smtplib.SMTPAuthenticationError:
        raise EmailError("Falha na autenticação SMTP. Verifique usuário e senha.")
    except smtplib.SMTPException as e:
        raise EmailError(f"Erro SMTP: {e}")
    except Exception as e:
        raise EmailError(f"Erro ao enviar e-mail: {e}")


def update_run_status(config: Config, status: Dict[str, Any]) -> Path:
    """
    Atualiza arquivo de status da execução.
    
    Args:
        config: Configurações do aplicativo
        status: Dicionário com status da execução
        
    Returns:
        Path do arquivo de status
    """
    status_file = config.output_dir / "last-run-status.json"
    
    # Garante que o diretório existe
    status_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Adiciona metadados
    status["updated_at"] = datetime.now().isoformat()
    status["version"] = "1.0.0"
    
    # Salva arquivo
    status_file.write_text(
        json.dumps(status, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    
    logger.debug(f"Status atualizado: {status_file}")
    return status_file


def send_error_notification(
    error_message: str,
    config: Config,
    include_logs: bool = True,
) -> bool:
    """
    Envia notificação de erro.
    
    Args:
        error_message: Mensagem de erro
        config: Configurações do aplicativo
        include_logs: Se deve incluir logs recentes
        
    Returns:
        True se notificação enviada
    """
    logger.warning(f"Enviando notificação de erro: {error_message}")
    
    if not validate_smtp_config(config):
        logger.warning("SMTP não configurado - não é possível enviar notificação de erro")
        return False
    
    try:
        body = f"""
⚠️ ERRO NO JORNAL-AGENT

Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

Erro:
{error_message}

---
Por favor, verifique os logs para mais detalhes.
"""
        
        send_email_fallback(
            subject="[ERRO] Jornal-Agent - Falha na execução",
            body=body,
            attachment_path=None,
            config=config,
        )
        
        return True
        
    except EmailError as e:
        logger.error(f"Não foi possível enviar notificação de erro: {e}")
        return False


def get_run_history(config: Config, limit: int = 10) -> list:
    """
    Obtém histórico de execuções.
    
    Args:
        config: Configurações do aplicativo
        limit: Número máximo de entradas
        
    Returns:
        Lista de execuções anteriores
    """
    history_file = config.output_dir / "run-history.json"
    
    if not history_file.exists():
        return []
    
    try:
        data = json.loads(history_file.read_text(encoding="utf-8"))
        return data[-limit:]
    except Exception as e:
        logger.warning(f"Erro ao ler histórico: {e}")
        return []


def append_to_history(config: Config, status: Dict[str, Any]) -> None:
    """
    Adiciona entrada ao histórico de execuções.
    
    Args:
        config: Configurações do aplicativo
        status: Status da execução
    """
    history_file = config.output_dir / "run-history.json"
    
    try:
        if history_file.exists():
            history = json.loads(history_file.read_text(encoding="utf-8"))
        else:
            history = []
        
        # Adiciona nova entrada
        entry = {
            "timestamp": datetime.now().isoformat(),
            "success": status.get("success", False),
            "error": status.get("error"),
            "phases": status.get("phases", {}),
        }
        history.append(entry)
        
        # Mantém apenas últimas 30 entradas
        history = history[-30:]
        
        history_file.write_text(
            json.dumps(history, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        
    except Exception as e:
        logger.warning(f"Erro ao atualizar histórico: {e}")


if __name__ == "__main__":
    # Teste do módulo
    from src.config import load_config
    
    config = load_config(dry_run=True)
    
    # Testa atualização de status
    status = {
        "success": True,
        "dry_run": True,
        "phases": {
            "download": {"success": True},
            "processing": {"success": True},
            "send": {"success": True},
        },
    }
    
    status_file = update_run_status(config, status)
    print(f"Status salvo em: {status_file}")
    
    # Mostra conteúdo
    print("\nConteúdo:")
    print(status_file.read_text())
