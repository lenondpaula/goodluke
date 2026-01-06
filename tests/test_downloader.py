"""
Testes para o módulo downloader.

Execute com: pytest tests/test_downloader.py -v
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
import asyncio

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.downloader import (
    download_pdf,
    get_pdf_filename,
    detect_captcha,
    CaptchaRequiredError,
    DownloadError,
    LoginError,
    PDFNotFoundError,
)
from src.config import load_config


class TestGetPdfFilename:
    """Testes para a função get_pdf_filename."""
    
    def test_filename_format(self):
        """Verifica se o nome do arquivo está no formato correto."""
        filename = get_pdf_filename()
        
        # Verifica padrão do nome
        assert filename.startswith("diario-")
        assert filename.endswith(".pdf")
        
        # Verifica data
        date_part = filename.replace("diario-", "").replace(".pdf", "")
        assert len(date_part) == 8
        assert date_part.isdigit()
    
    def test_filename_contains_today_date(self):
        """Verifica se o nome contém a data de hoje."""
        filename = get_pdf_filename()
        today = datetime.now().strftime("%Y%m%d")
        
        assert today in filename


class TestDownloadPdf:
    """Testes para a função download_pdf."""
    
    def test_dry_run_creates_dummy_file(self, tmp_path):
        """Verifica se o modo dry-run cria um arquivo de teste."""
        config = load_config(dry_run=True)
        config.data_dir = tmp_path
        
        pdf_path = download_pdf(config)
        
        assert pdf_path.exists()
        assert pdf_path.suffix == ".pdf"
        assert "diario-" in pdf_path.name
    
    def test_dry_run_file_has_content(self, tmp_path):
        """Verifica se o arquivo de teste tem conteúdo."""
        config = load_config(dry_run=True)
        config.data_dir = tmp_path
        
        pdf_path = download_pdf(config)
        
        content = pdf_path.read_bytes()
        assert len(content) > 0
        assert content.startswith(b"%PDF")
    
    def test_filename_matches_expected_pattern(self, tmp_path):
        """Verifica se o nome do arquivo segue o padrão esperado."""
        config = load_config(dry_run=True)
        config.data_dir = tmp_path
        
        pdf_path = download_pdf(config)
        
        expected_filename = get_pdf_filename()
        assert pdf_path.name == expected_filename


class TestDetectCaptcha:
    """Testes para a função detect_captcha."""
    
    @pytest.mark.asyncio
    async def test_no_captcha_returns_false(self):
        """Verifica que retorna False quando não há CAPTCHA."""
        mock_page = AsyncMock()
        mock_page.query_selector.return_value = None
        
        result = await detect_captcha(mock_page)
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_recaptcha_detected(self):
        """Verifica detecção de reCAPTCHA."""
        mock_page = AsyncMock()
        mock_element = AsyncMock()
        
        # Simula encontrar elemento de CAPTCHA
        async def mock_query_selector(selector):
            if "recaptcha" in selector.lower():
                return mock_element
            return None
        
        mock_page.query_selector.side_effect = mock_query_selector
        
        result = await detect_captcha(mock_page)
        
        assert result is True


class TestExceptions:
    """Testes para as exceções customizadas."""
    
    def test_captcha_required_error(self):
        """Verifica exceção CaptchaRequiredError."""
        with pytest.raises(CaptchaRequiredError) as exc_info:
            raise CaptchaRequiredError("CAPTCHA detectado")
        
        assert "CAPTCHA" in str(exc_info.value)
    
    def test_download_error(self):
        """Verifica exceção DownloadError."""
        with pytest.raises(DownloadError) as exc_info:
            raise DownloadError("Falha no download")
        
        assert "download" in str(exc_info.value).lower()
    
    def test_login_error(self):
        """Verifica exceção LoginError."""
        with pytest.raises(LoginError) as exc_info:
            raise LoginError("Credenciais inválidas")
        
        assert "Credenciais" in str(exc_info.value)
    
    def test_pdf_not_found_error(self):
        """Verifica exceção PDFNotFoundError."""
        with pytest.raises(PDFNotFoundError) as exc_info:
            raise PDFNotFoundError("PDF não encontrado")
        
        assert "PDF" in str(exc_info.value)


class TestIntegration:
    """Testes de integração (mocados)."""
    
    def test_full_download_flow_dry_run(self, tmp_path):
        """Testa o fluxo completo em modo dry-run."""
        config = load_config(dry_run=True)
        config.data_dir = tmp_path
        
        # Executa download
        pdf_path = download_pdf(config)
        
        # Verificações
        assert pdf_path.exists()
        assert pdf_path.parent == tmp_path
        assert pdf_path.suffix == ".pdf"
        
        # Verifica conteúdo
        content = pdf_path.read_bytes()
        assert b"PDF" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
