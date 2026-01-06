"""
Jornal-Agent - Módulo principal.

Agente automatizado para:
1. Download do PDF diário do jornal
2. Processamento e extração de texto com OCR
3. Geração de clipagem resumida via LLM
4. Envio do PDF e resumo via WhatsApp

Uso:
    python -m src.main           # Execução completa
    python -m src.main --dry-run # Modo de teste (não envia mensagens)
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from loguru import logger

from src.config import load_config, Config, ConfigError
from src.downloader import download_pdf, CaptchaRequiredError, DownloadError
from src.processor import process_pdf, ProcessingError
from src.whatsapp_client import send_media, WhatsAppError
from src.notifications import send_email_fallback, update_run_status


def setup_logging(verbose: bool = False) -> None:
    """
    Configura o sistema de logging.
    
    Args:
        verbose: Se True, loga em nível DEBUG
    """
    # Remove handlers padrão
    logger.remove()
    
    # Formato do log
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Console
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if verbose else "INFO",
        colorize=True,
    )
    
    # Arquivo de log
    log_file = Path(__file__).parent.parent / "output" / "jornal-agent.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format=log_format,
        level="DEBUG",
        rotation="1 week",
        retention="1 month",
        compression="gz",
    )


def download_phase(config: Config) -> Optional[Path]:
    """
    Fase 1: Download do PDF do jornal.
    
    Args:
        config: Configurações do aplicativo
        
    Returns:
        Path do PDF baixado ou None se falhar
    """
    logger.info("=" * 50)
    logger.info("FASE 1: Download do PDF")
    logger.info("=" * 50)
    
    try:
        pdf_path = download_pdf(config)
        logger.success(f"PDF baixado com sucesso: {pdf_path}")
        return pdf_path
        
    except CaptchaRequiredError as e:
        logger.error(f"CAPTCHA detectado - intervenção manual necessária: {e}")
        return None
        
    except DownloadError as e:
        logger.error(f"Erro no download: {e}")
        return None
        
    except Exception as e:
        logger.exception(f"Erro inesperado no download: {e}")
        return None


def process_phase(config: Config, pdf_path: Path) -> Optional[dict]:
    """
    Fase 2: Processamento do PDF e geração de clipagem.
    
    Args:
        config: Configurações do aplicativo
        pdf_path: Caminho do PDF a processar
        
    Returns:
        Resultado do processamento ou None se falhar
    """
    logger.info("=" * 50)
    logger.info("FASE 2: Processamento do PDF")
    logger.info("=" * 50)
    
    try:
        result = process_pdf(pdf_path, config)
        logger.success(f"PDF processado com sucesso")
        logger.info(f"  - Páginas processadas: {result.get('total_pages', 0)}")
        logger.info(f"  - Itens na clipagem: {result.get('total_items', 0)}")
        logger.info(f"  - Arquivo TXT: {result.get('txt_file', 'N/A')}")
        logger.info(f"  - Arquivo JSON: {result.get('json_file', 'N/A')}")
        return result
        
    except ProcessingError as e:
        logger.error(f"Erro no processamento: {e}")
        return None
        
    except Exception as e:
        logger.exception(f"Erro inesperado no processamento: {e}")
        return None


def send_phase(config: Config, pdf_path: Path, result: dict) -> bool:
    """
    Fase 3: Envio do PDF e resumo via WhatsApp.
    
    Args:
        config: Configurações do aplicativo
        pdf_path: Caminho do PDF a enviar
        result: Resultado do processamento com clipagem
        
    Returns:
        True se envio bem-sucedido, False caso contrário
    """
    logger.info("=" * 50)
    logger.info("FASE 3: Envio via WhatsApp")
    logger.info("=" * 50)
    
    if config.dry_run:
        logger.warning("Modo DRY-RUN: Simulando envio (nenhuma mensagem será enviada)")
        logger.info(f"  - Destinatário: {config.whatsapp_recipient or '[não configurado]'}")
        logger.info(f"  - PDF: {pdf_path}")
        logger.info(f"  - Resumo: {len(result.get('summary_text', ''))} caracteres")
        return True
    
    try:
        # Prepara a mensagem
        today = datetime.now().strftime("%d/%m/%Y")
        summary_text = result.get("summary_text", "Clipagem não disponível")
        message = f"📰 *Clipagem do Diário - {today}*\n\n{summary_text}"
        
        # Envia via WhatsApp
        send_result = send_media(
            to_phone=config.whatsapp_recipient,
            pdf_path=pdf_path,
            message_text=message,
            config=config,
        )
        
        logger.success(f"Mensagem enviada com sucesso!")
        logger.info(f"  - Message ID: {send_result.get('message_id', 'N/A')}")
        return True
        
    except WhatsAppError as e:
        logger.error(f"Erro no envio WhatsApp: {e}")
        logger.info("Tentando fallback por e-mail...")
        
        # Tenta fallback por e-mail
        try:
            send_email_fallback(
                subject=f"Clipagem do Diário - {datetime.now().strftime('%d/%m/%Y')}",
                body=result.get("summary_text", ""),
                attachment_path=pdf_path,
                config=config,
            )
            logger.success("E-mail de fallback enviado com sucesso!")
            return True
        except Exception as email_error:
            logger.error(f"Fallback por e-mail também falhou: {email_error}")
            return False
            
    except Exception as e:
        logger.exception(f"Erro inesperado no envio: {e}")
        return False


def main(dry_run: bool = False, verbose: bool = False) -> int:
    """
    Função principal do agente.
    
    Args:
        dry_run: Se True, não envia mensagens reais
        verbose: Se True, ativa logs detalhados
        
    Returns:
        Código de saída (0 = sucesso, 1 = erro)
    """
    setup_logging(verbose)
    
    logger.info("=" * 60)
    logger.info("JORNAL-AGENT - Iniciando execução")
    logger.info(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Modo: {'DRY-RUN (teste)' if dry_run else 'PRODUÇÃO'}")
    logger.info("=" * 60)
    
    status = {
        "timestamp": datetime.now().isoformat(),
        "dry_run": dry_run,
        "phases": {},
        "success": False,
        "error": None,
    }
    
    try:
        # Carrega configurações
        config = load_config(dry_run=dry_run)
        
        # Fase 1: Download
        pdf_path = download_phase(config)
        status["phases"]["download"] = {
            "success": pdf_path is not None,
            "file": str(pdf_path) if pdf_path else None,
        }
        
        if not pdf_path:
            status["error"] = "Falha no download do PDF"
            update_run_status(config, status)
            return 1
        
        # Fase 2: Processamento
        result = process_phase(config, pdf_path)
        status["phases"]["processing"] = {
            "success": result is not None,
            "total_pages": result.get("total_pages", 0) if result else 0,
            "total_items": result.get("total_items", 0) if result else 0,
        }
        
        if not result:
            status["error"] = "Falha no processamento do PDF"
            update_run_status(config, status)
            return 1
        
        # Fase 3: Envio
        send_success = send_phase(config, pdf_path, result)
        status["phases"]["send"] = {
            "success": send_success,
            "method": "dry-run" if dry_run else "whatsapp",
        }
        
        if not send_success:
            status["error"] = "Falha no envio da mensagem"
            update_run_status(config, status)
            return 1
        
        # Sucesso!
        status["success"] = True
        update_run_status(config, status)
        
        logger.info("=" * 60)
        logger.success("JORNAL-AGENT - Execução concluída com sucesso!")
        logger.info("=" * 60)
        
        return 0
        
    except ConfigError as e:
        logger.error(f"Erro de configuração: {e}")
        status["error"] = str(e)
        return 1
        
    except Exception as e:
        logger.exception(f"Erro inesperado: {e}")
        status["error"] = str(e)
        return 1


def parse_args() -> argparse.Namespace:
    """Parse argumentos da linha de comando."""
    parser = argparse.ArgumentParser(
        description="Jornal-Agent - Automação de clipagem de jornal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python -m src.main              # Execução normal
  python -m src.main --dry-run    # Modo de teste
  python -m src.main -v           # Logs detalhados
        """,
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Modo de teste: não envia mensagens reais",
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Ativa logs detalhados (DEBUG)",
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    sys.exit(main(dry_run=args.dry_run, verbose=args.verbose))
