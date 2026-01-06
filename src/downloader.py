"""
Jornal-Agent - Módulo de Download.

Este módulo implementa o download automatizado do PDF do jornal
usando Playwright para automação de navegador headless.

Funcionalidades:
- Login automático na área restrita
- Download do PDF diário
- Retry com backoff exponencial
- Detecção de CAPTCHA
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
import time

from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from playwright.async_api import TimeoutError as PlaywrightTimeout
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config


class DownloadError(Exception):
    """Erro genérico durante o download."""
    pass


class CaptchaRequiredError(Exception):
    """CAPTCHA detectado - requer intervenção manual."""
    pass


class LoginError(Exception):
    """Erro durante o processo de login."""
    pass


class PDFNotFoundError(Exception):
    """PDF não encontrado na página."""
    pass


def get_pdf_filename() -> str:
    """
    Gera o nome do arquivo PDF com a data atual.
    
    Returns:
        Nome do arquivo no formato diario-YYYYMMDD.pdf
    """
    today = datetime.now().strftime("%Y%m%d")
    return f"diario-{today}.pdf"


async def detect_captcha(page: Page) -> bool:
    """
    Detecta se a página contém um CAPTCHA.
    
    Args:
        page: Página do Playwright
        
    Returns:
        True se CAPTCHA detectado, False caso contrário
    """
    captcha_indicators = [
        # Google reCAPTCHA
        'iframe[src*="recaptcha"]',
        'iframe[src*="captcha"]',
        '.g-recaptcha',
        '#recaptcha',
        # hCaptcha
        'iframe[src*="hcaptcha"]',
        '.h-captcha',
        # Genéricos
        'img[alt*="captcha" i]',
        'input[name*="captcha" i]',
        '[class*="captcha" i]',
        '[id*="captcha" i]',
    ]
    
    for selector in captcha_indicators:
        try:
            element = await page.query_selector(selector)
            if element:
                logger.warning(f"CAPTCHA detectado: {selector}")
                return True
        except Exception:
            continue
    
    return False


async def wait_for_download(page: Page, download_path: Path, timeout: int = 60000) -> Path:
    """
    Aguarda o download de um arquivo.
    
    Args:
        page: Página do Playwright
        download_path: Diretório de destino
        timeout: Timeout em milissegundos
        
    Returns:
        Path do arquivo baixado
        
    Raises:
        DownloadError: Se o download falhar
    """
    try:
        async with page.expect_download(timeout=timeout) as download_info:
            # O clique no botão de download deve ser feito antes de chamar esta função
            pass
        
        download = await download_info.value
        
        # Define o caminho final
        filename = get_pdf_filename()
        final_path = download_path / filename
        
        # Salva o arquivo
        await download.save_as(final_path)
        
        logger.info(f"Arquivo baixado: {final_path}")
        return final_path
        
    except PlaywrightTimeout:
        raise DownloadError("Timeout aguardando download")
    except Exception as e:
        raise DownloadError(f"Erro durante download: {e}")


async def perform_login(
    page: Page,
    login_url: str,
    username: str,
    password: str,
    timeout: int = 30000,
) -> bool:
    """
    Realiza o login na área restrita do jornal.
    
    Args:
        page: Página do Playwright
        login_url: URL da página de login
        username: Nome de usuário
        password: Senha
        timeout: Timeout em milissegundos
        
    Returns:
        True se login bem-sucedido
        
    Raises:
        CaptchaRequiredError: Se CAPTCHA for detectado
        LoginError: Se o login falhar
    """
    logger.info(f"Acessando página de login: {login_url}")
    
    try:
        await page.goto(login_url, wait_until="networkidle", timeout=timeout)
    except PlaywrightTimeout:
        raise LoginError(f"Timeout ao carregar página de login: {login_url}")
    
    # Verifica CAPTCHA
    if await detect_captcha(page):
        raise CaptchaRequiredError("CAPTCHA detectado na página de login")
    
    # Tenta encontrar os campos de login
    # Estes seletores devem ser ajustados para o jornal específico
    login_selectors = [
        # Seletores comuns de username
        ('input[name="username"]', 'input[name="password"]', 'button[type="submit"]'),
        ('input[name="email"]', 'input[name="password"]', 'button[type="submit"]'),
        ('input[name="user"]', 'input[name="pass"]', 'button[type="submit"]'),
        ('input[id="username"]', 'input[id="password"]', 'button[type="submit"]'),
        ('input[id="email"]', 'input[id="password"]', 'button[type="submit"]'),
        ('input[type="email"]', 'input[type="password"]', 'button[type="submit"]'),
        ('input[type="text"]', 'input[type="password"]', 'button[type="submit"]'),
        ('#login-username', '#login-password', '#login-submit'),
        ('.login-username', '.login-password', '.login-submit'),
    ]
    
    for user_sel, pass_sel, submit_sel in login_selectors:
        try:
            user_input = await page.query_selector(user_sel)
            pass_input = await page.query_selector(pass_sel)
            submit_btn = await page.query_selector(submit_sel)
            
            if user_input and pass_input and submit_btn:
                logger.debug(f"Usando seletores: {user_sel}, {pass_sel}, {submit_sel}")
                
                # Preenche os campos
                await user_input.fill(username)
                await pass_input.fill(password)
                
                # Clica no botão de submit
                await submit_btn.click()
                
                # Aguarda navegação
                await page.wait_for_load_state("networkidle", timeout=timeout)
                
                # Verifica se login foi bem-sucedido
                # (verifica se ainda está na página de login ou se há mensagem de erro)
                current_url = page.url
                if "login" not in current_url.lower():
                    logger.info("Login realizado com sucesso!")
                    return True
                
                # Verifica mensagens de erro
                error_selectors = [
                    '.error', '.alert-danger', '.login-error', 
                    '[class*="error"]', '[class*="invalid"]',
                ]
                for err_sel in error_selectors:
                    error_elem = await page.query_selector(err_sel)
                    if error_elem:
                        error_text = await error_elem.text_content()
                        raise LoginError(f"Login falhou: {error_text}")
                
        except LoginError:
            raise
        except CaptchaRequiredError:
            raise
        except Exception as e:
            logger.debug(f"Seletores {user_sel} não funcionaram: {e}")
            continue
    
    raise LoginError("Não foi possível encontrar os campos de login na página")


async def find_and_download_pdf(
    page: Page,
    pdf_url: str,
    download_path: Path,
    timeout: int = 60000,
) -> Path:
    """
    Navega até a página do PDF e realiza o download.
    
    Args:
        page: Página do Playwright
        pdf_url: URL da página com o PDF
        download_path: Diretório de destino
        timeout: Timeout em milissegundos
        
    Returns:
        Path do arquivo PDF baixado
        
    Raises:
        PDFNotFoundError: Se o PDF não for encontrado
        DownloadError: Se o download falhar
    """
    logger.info(f"Navegando para página do PDF: {pdf_url}")
    
    try:
        await page.goto(pdf_url, wait_until="networkidle", timeout=timeout)
    except PlaywrightTimeout:
        raise PDFNotFoundError(f"Timeout ao carregar página do PDF: {pdf_url}")
    
    # Verifica CAPTCHA
    if await detect_captcha(page):
        raise CaptchaRequiredError("CAPTCHA detectado na página do PDF")
    
    # Seletores para botões/links de download
    download_selectors = [
        'a[href$=".pdf"]',
        'a[download]',
        'a[href*="download"]',
        'button[class*="download"]',
        'a[class*="download"]',
        '.pdf-download',
        '#download-pdf',
        'a[title*="download" i]',
        'a[title*="baixar" i]',
        'button[title*="download" i]',
    ]
    
    # Prepara para capturar o download
    filename = get_pdf_filename()
    final_path = download_path / filename
    
    for selector in download_selectors:
        try:
            download_elem = await page.query_selector(selector)
            if download_elem:
                logger.debug(f"Tentando download com seletor: {selector}")
                
                # Configura o download
                async with page.expect_download(timeout=timeout) as download_info:
                    await download_elem.click()
                
                download = await download_info.value
                await download.save_as(final_path)
                
                # Verifica se o arquivo foi baixado corretamente
                if final_path.exists() and final_path.stat().st_size > 0:
                    logger.success(f"PDF baixado com sucesso: {final_path}")
                    return final_path
                    
        except PlaywrightTimeout:
            logger.debug(f"Timeout com seletor {selector}")
            continue
        except Exception as e:
            logger.debug(f"Erro com seletor {selector}: {e}")
            continue
    
    # Tenta encontrar link direto para PDF
    try:
        pdf_links = await page.query_selector_all('a[href]')
        for link in pdf_links:
            href = await link.get_attribute('href')
            if href and '.pdf' in href.lower():
                logger.debug(f"Encontrado link PDF: {href}")
                
                async with page.expect_download(timeout=timeout) as download_info:
                    await link.click()
                
                download = await download_info.value
                await download.save_as(final_path)
                
                if final_path.exists() and final_path.stat().st_size > 0:
                    logger.success(f"PDF baixado com sucesso: {final_path}")
                    return final_path
                    
    except Exception as e:
        logger.debug(f"Erro ao buscar links PDF: {e}")
    
    raise PDFNotFoundError("Não foi possível encontrar o PDF para download")


async def download_pdf_async(config: Config) -> Path:
    """
    Implementação assíncrona do download do PDF.
    
    Args:
        config: Configurações do aplicativo
        
    Returns:
        Path do PDF baixado
        
    Raises:
        CaptchaRequiredError: Se CAPTCHA for detectado
        DownloadError: Se o download falhar
    """
    timeout = config.timeout * 1000  # Converte para ms
    
    async with async_playwright() as p:
        logger.info("Iniciando navegador headless...")
        
        browser = await p.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ],
        )
        
        context = await browser.new_context(
            accept_downloads=True,
            viewport={'width': 1920, 'height': 1080},
            user_agent=(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
        )
        
        page = await context.new_page()
        
        try:
            # Passo 1: Login
            logger.info("Iniciando processo de login...")
            await perform_login(
                page=page,
                login_url=config.jornal_login_url,
                username=config.jornal_user,
                password=config.jornal_pass,
                timeout=timeout,
            )
            
            # Passo 2: Download do PDF
            logger.info("Buscando PDF para download...")
            pdf_path = await find_and_download_pdf(
                page=page,
                pdf_url=config.jornal_pdf_url,
                download_path=config.data_dir,
                timeout=timeout,
            )
            
            return pdf_path
            
        finally:
            await context.close()
            await browser.close()
            logger.info("Navegador fechado")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((DownloadError, PDFNotFoundError, LoginError)),
    before_sleep=lambda retry_state: logger.warning(
        f"Tentativa {retry_state.attempt_number} falhou. "
        f"Aguardando antes da próxima tentativa..."
    ),
)
def download_pdf_with_retry(config: Config) -> Path:
    """
    Download do PDF com retry automático.
    
    Args:
        config: Configurações do aplicativo
        
    Returns:
        Path do PDF baixado
    """
    return asyncio.run(download_pdf_async(config))


def download_pdf(config: Config) -> Path:
    """
    Função principal de download do PDF.
    
    Esta função realiza:
    1. Login automatizado na área restrita do jornal
    2. Navegação até a página do PDF
    3. Download do arquivo para data/diario-YYYYMMDD.pdf
    4. Retry automático em caso de falha (até 3 tentativas)
    
    Args:
        config: Configurações do aplicativo
        
    Returns:
        Path do PDF baixado
        
    Raises:
        CaptchaRequiredError: Se CAPTCHA for detectado
        DownloadError: Se o download falhar após todas as tentativas
    """
    logger.info("Iniciando download do PDF...")
    
    # Modo dry-run: retorna um path fictício
    if config.dry_run:
        logger.warning("Modo DRY-RUN: Simulando download")
        dummy_path = config.data_dir / get_pdf_filename()
        
        # Cria um arquivo vazio para teste
        dummy_path.parent.mkdir(parents=True, exist_ok=True)
        dummy_path.write_bytes(b"%PDF-1.4 dummy")
        
        logger.info(f"Arquivo de teste criado: {dummy_path}")
        return dummy_path
    
    try:
        return download_pdf_with_retry(config)
    except Exception as e:
        logger.error(f"Download falhou após todas as tentativas: {e}")
        raise


if __name__ == "__main__":
    # Teste do módulo
    from src.config import load_config
    
    config = load_config(dry_run=True)
    pdf_path = download_pdf(config)
    print(f"PDF: {pdf_path}")
