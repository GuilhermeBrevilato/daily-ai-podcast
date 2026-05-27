# 🎙️ Daily AI Podcast

> Sistema que gera automaticamente dois podcasts diários usando IA, entregues via Telegram todo dia de madrugada.

---

## 🚀 O que faz

- 🔍 **Pesquisa** automaticamente as principais notícias e estudos de IA
- 🧠 **Resume e analisa** o conteúdo com GPT-4o, com contexto, tensões e perguntas provocativas
- 🎙️ **Gera áudio** no NotebookLM com dois apresentadores debatendo o conteúdo
- 📱 **Envia o podcast** direto no Telegram para todos os destinatários configurados

---

## 📋 Podcasts gerados

| Podcast | Horário | Conteúdo |
|---------|---------|----------|
| 🔬 Pesquisas de IA | 03:30 | Papers, estudos e pesquisas científicas de IA |
| 📰 Notícias de Tech | 04:10 | Novidades, startups e tendências de tecnologia mundial |

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|------------|-----|
| Python 3.12 | Linguagem principal |
| GPT-4o (OpenAI) | Pesquisa, resumo e análise de conteúdo |
| NotebookLM (Google) | Geração de áudio com dois apresentadores IA |
| Selenium | Automação do browser |
| Telegram Bot API | Entrega do podcast |
| ffmpeg | Compressão do áudio |
| LaunchAgent (Mac) | Agendamento automático diário |

---

## ⚙️ Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/GuilhermeBrevilato/daily-ai-podcast.git
cd daily-ai-podcast

# 2. Instale as dependências Python
pip install -r requirements.txt

# 3. Instale o ffmpeg
brew install ffmpeg

# 4. Configure as credenciais
cp .env.example .env
cp .env.example .env.noticias
# Edite os arquivos .env com suas chaves
```

---

## 🔑 Configuração do .env

```env
# OpenAI
OPENAI_API_KEY=sua-chave-openai

# Telegram
TELEGRAM_BOT_TOKEN=token-do-seu-bot
TELEGRAM_CHAT_ID=seu-chat-id
TELEGRAM_CHAT_ID_2=chat-id-opcional

# NotebookLM (conta Google)
NOTEBOOKLM_EMAIL=seu-email@gmail.com
NOTEBOOKLM_PASSWORD=sua-senha

# Configurações
POLLING_INTERVAL_MINUTES=3
MAX_POLLING_ATTEMPTS=8
SCHEDULE_TIME=03:30

# Tópicos de pesquisa (separados por |)
RESEARCH_TOPICS=agentes de IA papers científicos|OpenAI Anthropic Google DeepMind research|large language models estudos acadêmicos
RESULTS_PER_TOPIC=10
```

### Como obter o Telegram Chat ID
1. Abra o Telegram e fale com **@userinfobot**
2. Ele responde automaticamente com seu **Id**

### Como criar um bot no Telegram
1. Fale com **@BotFather**
2. Digite `/newbot` e siga as instruções
3. Copie o token gerado

---

## 🚀 Como rodar

```bash
# Teste imediato — pesquisas de IA
python3 main.py --agora

# Teste imediato — notícias de tecnologia
python3 main_noticias.py --agora

# Modo agendado (roda automaticamente no horário configurado)
python3 main.py
```

---

## ⏰ Agendamento automático no Mac

```bash
# Configura o LaunchAgent para rodar às 03:30
launchctl load ~/Library/LaunchAgents/com.dailypodcast.pesquisas.plist

# Configura o LaunchAgent para rodar às 04:10
launchctl load ~/Library/LaunchAgents/com.dailypodcast.noticias.plist

# Configura o Mac para acordar automaticamente às 03:25
sudo pmset repeat wakeorpoweron MTWRFSU 03:25:00
```

---

## 📁 Estrutura do projeto

```
daily-ai-podcast/
├── main.py                   # Orquestrador — pesquisas científicas
├── main_noticias.py          # Orquestrador — notícias de tecnologia
├── modules/
│   ├── pesquisa.py           # Busca e resumo com GPT-4o
│   ├── notebooklm.py         # Automação completa do NotebookLM
│   ├── visao_selenium.py     # Agente de visão + Selenium
│   └── telegram_sender.py   # Envio via Telegram (múltiplos destinatários)
├── .env.example              # Template de configuração
├── requirements.txt          # Dependências Python
└── README.md
```

---

## 🔄 Fluxo completo

```
03:25 → Mac acorda automaticamente
03:30 → Pesquisa artigos e papers de IA
        GPT-4o resume e analisa o conteúdo
        Chrome abre o NotebookLM automaticamente
        Cria notebook e insere o resumo
        Clica em gerar áudio
        Aguarda ~18 minutos
        Baixa e comprime o áudio
        🎙️ Envia para todos no Telegram

04:10 → Mesmo fluxo para notícias de tecnologia
        🎙️ Podcast de notícias chega no Telegram
```

---

## 💰 Custo estimado

| Item | Custo/mês |
|------|-----------|
| GPT-4o (pesquisa + resumo) | ~$2.00 |
| GPT-4o (visão Selenium) | ~$1.00 |
| **Total** | **~$3-4/mês** |

> NotebookLM, Telegram e Selenium são gratuitos.

---

## ⚠️ Requisitos

- Mac com **Google Chrome** instalado
- Conta Google com acesso ao **NotebookLM**
- Chave de API da **OpenAI** (GPT-4o)
- **Bot do Telegram** configurado
- Mac **conectado na tomada** para o wake automático funcionar

---

## 📝 Observações importantes

- O Chrome usa um perfil separado para manter o login do Google
- O `caffeinate` impede o Mac de dormir durante a geração do áudio
- Os arquivos `.env` **nunca** são commitados no repositório
- O áudio é comprimido de ~50MB para ~10MB antes do envio


---

Feito com ☕ e muito Python 🐍
