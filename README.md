# Jornal-Agent 📰

Agente automatizado para download, processamento e envio de clipagem de jornal via WhatsApp.

## 🎯 Funcionalidades

- **Download automatizado**: Login e download do PDF do jornal usando Playwright (headless browser)
- **Extração inteligente**: Extração de texto nativo + OCR para páginas escaneadas
- **Clipagem com IA**: Resumo automático usando LLM (OpenAI, DeepSeek, etc.)
- **Envio via WhatsApp**: Envio do PDF e resumo via WhatsApp Cloud API
- **Fallback por e-mail**: Envio alternativo por SMTP se WhatsApp falhar
- **Execução agendada**: GitHub Actions roda diariamente às 06:00 BRT

## 📁 Estrutura do Projeto

```
├── .github/
│   └── workflows/
│       └── daily-run.yml      # Workflow do GitHub Actions
├── src/
│   ├── __init__.py
│   ├── main.py                # Ponto de entrada principal
│   ├── config.py              # Configuração e validação de env vars
│   ├── downloader.py          # Download do PDF com Playwright
│   ├── processor.py           # Extração de texto e OCR
│   ├── llm_client.py          # Integração com LLM
│   ├── whatsapp_client.py     # Envio via WhatsApp Cloud API
│   └── notifications.py       # Fallback por e-mail e status
├── tests/
│   ├── __init__.py
│   └── test_downloader.py     # Testes do downloader
├── data/                      # PDFs baixados
├── output/                    # Arquivos de saída (clipagem, logs)
├── requirements.txt           # Dependências Python
└── README.md                  # Este arquivo
```

## 🔒 Configuração de Secrets

### GitHub Secrets (Obrigatórios)

Adicione os seguintes secrets no seu repositório GitHub:
**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Descrição |
|--------|-----------|
| `JORNAL_USER` | Usuário para login no jornal |
| `JORNAL_PASS` | Senha para login no jornal |
| `LLM_API_KEY` | Chave da API do LLM (OpenAI, DeepSeek, etc.) |
| `WHATSAPP_TOKEN` | Token de acesso da WhatsApp Cloud API |
| `WHATSAPP_PHONE_ID` | ID do número de telefone do WhatsApp Business |

### GitHub Secrets (Opcionais)

| Secret | Descrição | Padrão |
|--------|-----------|--------|
| `JORNAL_LOGIN_URL` | URL da página de login | Configurar no código |
| `JORNAL_PDF_URL` | URL da página do PDF | Configurar no código |
| `LLM_MODEL` | Modelo do LLM | `gpt-4o-mini` |
| `LLM_BASE_URL` | URL base da API (para DeepSeek, etc.) | - |
| `WHATSAPP_RECIPIENT` | Número do destinatário WhatsApp | - |
| `SMTP_HOST` | Servidor SMTP para fallback | - |
| `SMTP_PORT` | Porta SMTP | `587` |
| `SMTP_USER` | Usuário SMTP | - |
| `SMTP_PASS` | Senha SMTP | - |
| `EMAIL_FROM` | E-mail remetente | - |
| `EMAIL_TO` | E-mail destinatário | - |

## 🚀 Instalação e Uso

### Pré-requisitos

- Python 3.11+
- Tesseract OCR
- Chromium (para Playwright)

### Instalação Local (Codespaces)

```bash
# 1. Instalar dependências Python
pip install -r requirements.txt

# 2. Instalar Playwright e navegador
playwright install chromium
playwright install-deps chromium

# 3. Instalar Tesseract OCR (já instalado no Codespaces)
sudo apt install tesseract-ocr tesseract-ocr-por

# 4. Configurar variáveis de ambiente (criar arquivo .env)
cat > .env << EOF
JORNAL_USER=seu_usuario
JORNAL_PASS=sua_senha
LLM_API_KEY=sua_chave_api
WHATSAPP_TOKEN=seu_token
WHATSAPP_PHONE_ID=seu_phone_id
WHATSAPP_RECIPIENT=5511999999999
EOF
```

### Executar Localmente

```bash
# Modo de teste (dry-run) - NÃO envia mensagens reais
python -m src.main --dry-run

# Modo de teste com logs detalhados
python -m src.main --dry-run --verbose

# Execução completa (produção)
python -m src.main
```

### Executar Testes

```bash
pytest tests/ -v
```

## ⏰ Execução Agendada (GitHub Actions)

O workflow `.github/workflows/daily-run.yml` executa automaticamente:

- **Horário**: 06:00 BRT (09:00 UTC) todos os dias
- **Trigger manual**: Acesse Actions → Daily Jornal Agent → Run workflow

Para executar manualmente em modo dry-run:
1. Vá em Actions → Daily Jornal Agent
2. Clique em "Run workflow"
3. Selecione `dry_run: true`
4. Clique em "Run workflow"

## 📤 Arquivos de Saída

Após cada execução, os seguintes arquivos são gerados em `output/`:

| Arquivo | Descrição |
|---------|-----------|
| `clipagem-YYYYMMDD.txt` | Clipagem formatada em texto |
| `clipagem-YYYYMMDD.json` | Clipagem com metadados em JSON |
| `verification-YYYYMMDD.txt` | Relatório de verificação página a página |
| `last-run-status.json` | Status da última execução |
| `jornal-agent.log` | Logs detalhados |

## 🔧 Configuração do WhatsApp Cloud API

### 1. Criar conta no Meta for Developers

1. Acesse [developers.facebook.com](https://developers.facebook.com)
2. Crie um App do tipo "Business"
3. Adicione o produto "WhatsApp"

### 2. Configurar WhatsApp Business

1. Vá em WhatsApp → API Setup
2. Copie o **Phone number ID** → `WHATSAPP_PHONE_ID`
3. Gere um **Permanent Access Token** → `WHATSAPP_TOKEN`
4. Adicione o número do destinatário na lista de permitidos

### 3. Testar envio

```bash
# Teste de envio (substitua os valores)
curl -X POST "https://graph.facebook.com/v18.0/YOUR_PHONE_ID/messages" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"messaging_product":"whatsapp","to":"5511999999999","type":"text","text":{"body":"Teste"}}'
```

## 🤖 Configuração do LLM

### OpenAI

```env
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

### DeepSeek

```env
LLM_API_KEY=sk-...
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1
```

### Personalizar Prompt

Edite o `DEFAULT_PROMPT_TEMPLATE` em [src/llm_client.py](src/llm_client.py) para customizar os critérios de seleção e formato de saída da clipagem.

## 🛡️ Segurança

- ⚠️ **NUNCA** commite credenciais no código
- Use apenas GitHub Secrets ou arquivo `.env` local
- O arquivo `.env` está no `.gitignore`
- Revise logs antes de compartilhar (podem conter dados sensíveis)

## 📋 Checklist de Produção

- [ ] Adicionar todos os secrets obrigatórios no GitHub
- [ ] Testar localmente com `--dry-run`
- [ ] Executar workflow manualmente para validar
- [ ] Revisar `output/verification-*.txt` para verificar extração
- [ ] Confirmar que o uso do PDF está autorizado pelo jornal/contrato

## 🐛 Troubleshooting

### CAPTCHA detectado

Se o jornal implementar CAPTCHA, o agente irá parar e logar o erro. Neste caso:
1. Verifique se as credenciais estão corretas
2. Faça login manual para desbloquear a conta
3. Considere usar cookies persistentes

### Tesseract não encontrado

```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

### Playwright não funciona

```bash
playwright install chromium
playwright install-deps chromium
```

### Rate limit do LLM

O código implementa retry automático com backoff exponencial. Se persistir, considere:
- Aumentar intervalo entre execuções
- Usar modelo mais econômico
- Implementar cache de resultados

## 📄 Licença

Uso interno. Verifique termos de uso do jornal antes de automatizar.

---

Desenvolvido com ❤️ usando GitHub Copilot
