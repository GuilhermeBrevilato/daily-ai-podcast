"""
Módulo 4: Envio via Telegram
- Envia o áudio gerado para o chat do Telegram
"""

import os
import logging
import asyncio
from pathlib import Path
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


async def _enviar_audio_async(caminho_audio: str, caption: str):
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))

    destinatarios = [
        os.getenv("TELEGRAM_CHAT_ID"),
        os.getenv("TELEGRAM_CHAT_ID_2", ""),
        os.getenv("TELEGRAM_CHAT_ID_3", ""),
    ]

    for chat_id in destinatarios:
        if not chat_id:
            continue
        for tentativa in range(3):  # tenta 3 vezes
            try:
                with open(caminho_audio, "rb") as audio_file:
                    await bot.send_audio(
                        chat_id=chat_id,
                        audio=audio_file,
                        caption=caption,
                        title="🎙️ Podcast Diário IA & Tech",
                        performer="Daily AI Bot",
                    )
                logger.info(f"✅ Áudio enviado para: {chat_id}")
                break  # sucesso, sai do loop
            except Exception as e:
                logger.error(f"❌ Tentativa {tentativa+1} falhou para {chat_id}: {e}")
                if tentativa < 2:
                    await asyncio.sleep(5)  # aguarda 5s antes de tentar de novo


async def _enviar_mensagem_async(texto: str):
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    await bot.send_message(chat_id=chat_id, text=texto, parse_mode="Markdown")


def enviar_audio_telegram(caminho_audio: str, data_str: str) -> bool:
    """Envia o áudio para o Telegram."""
    caption = (
        f"🎙️ *Seu podcast diário está pronto!*\n"
        f"📅 {data_str}\n\n"
        f"📌 Conteúdo: Top 10 pesquisas de IA + Top 10 notícias de tecnologia\n"
        f"🤖 Gerado automaticamente pelo NotebookLM"
    )
    
    try:
        asyncio.run(_enviar_audio_async(caminho_audio, caption))
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao enviar áudio: {e}")
        return False


def enviar_notificacao_erro(erro: str) -> None:
    """Envia mensagem de erro no Telegram."""
    try:
        mensagem = f"❌ *Erro no podcast diário*\n\n```{erro}```"
        asyncio.run(_enviar_mensagem_async(mensagem))
    except Exception as e:
        logger.error(f"Erro ao enviar notificação: {e}")


def enviar_notificacao_inicio() -> None:
    """Avisa que o processo começou."""
    try:
        mensagem = "🚀 *Iniciando geração do podcast diário...*\nVocê receberá o áudio em breve!"
        asyncio.run(_enviar_mensagem_async(mensagem))
    except Exception as e:
        logger.error(f"Erro ao enviar notificação de início: {e}")
