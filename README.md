# 🎙️ Daily AI Podcast — Guia de Configuração

Sistema que gera automaticamente um podcast diário com as principais pesquisas de IA e notícias de tecnologia, usando NotebookLM + GPT-4o, entregue via Telegram todo dia às 6h.

---

## 📋 Pré-requisitos

- Python 3.11+
- Google Chrome instalado
- Conta Google com acesso ao NotebookLM
- Chave de API da OpenAI (GPT-4o)
- Bot do Telegram configurado

---

## ⚙️ Instalação

```bash
# 1. Clone ou baixe o projeto
cd daily-podcast

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

---

## 🔑 Configurando o .env

```env
OPENAI_API_KEY=sk-...          # Sua chave OpenAI
TELEGRAM_BOT_TOKEN=...         # Token do seu bot
TELEGRAM_CHAT_ID=...           # Seu chat ID
NOTEBOOKLM_EMAIL=...           # Email da conta Google
NOTEBOOKLM_PASSWORD=...        # Senha da conta Google
```

### Como obter o TELEGRAM_CHAT_ID:
1. Abra o Telegram e fale com @userinfobot
2. Ele vai te responder com seu Chat ID

### Como criar um bot no Telegram:
1. Fale com @BotFather
2. Digite /newbot e siga as instruções
3. Copie o token gerado

---

## 🚀 Executando

```bash
# Testar agora (execução imediata)
python main.py --agora

# Rodar em modo agendado (todo dia às 06:00)
python main.py

# Testar apenas o módulo de pesquisa
python modules/pesquisa.py
```

---

## 🗂️ Estrutura do Projeto

```
daily-podcast/
├── main.py                    # Orquestrador principal
├── requirements.txt           # Dependências
├── .env.example               # Template de configuração
├── modules/
│   ├── pesquisa.py            # Busca e resumo de conteúdo
│   ├── visao_selenium.py      # IA visual + Selenium
│   ├── notebooklm.py          # Automação do NotebookLM
│   └── telegram_sender.py     # Envio via Telegram
├── output/                    # Resumos e áudios gerados
└── logs/                      # Logs de execução
```

---

## 💰 Custo estimado com GPT-4o

| Uso | Chamadas/dia | Custo |
|-----|-------------|-------|
| Pesquisa + resumos | ~5 | ~$0.02 |
| Visão (prints Selenium) | ~10 | ~$0.05 |
| Polling de status | ~4 | ~$0.03 |
| **Total** | | **~$0.10/dia (~$3/mês)** |

---

## 🔧 Personalizando os tópicos

No arquivo `.env`, edite:
```env
RESEARCH_TOPICS=agentes de inteligência artificial|notícias de tecnologia|sua categoria aqui
RESULTS_PER_TOPIC=10
```

---

## ⚠️ Observações importantes

1. **Autenticação Google**: Se usar verificação em duas etapas, pode ser necessário gerar uma senha de app
2. **Chrome visível**: Na primeira execução, deixe o Chrome visível para verificar se o login funcionou
3. **NotebookLM**: O tempo de geração do áudio varia (30min a 2h). O sistema verifica a cada 15 minutos
4. **Logs**: Verifique a pasta `logs/` se algo der errado — há prints de erro salvos

---

## 🐛 Troubleshooting

**Erro de login Google**: O Google pode bloquear logins automáticos. Acesse manualmente uma vez e marque "lembrar dispositivo".

**Selenium não encontra elemento**: O NotebookLM mudou a interface. Os logs mostram o print da tela no momento do erro.

**Áudio não baixa**: Verifique a pasta Downloads do sistema — o Chrome pode ter baixado lá.
