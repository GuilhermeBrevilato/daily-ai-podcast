"""
🎙️ Daily Tech News Podcast — Orquestrador de Notícias
"""

import os
import time
import logging
import schedule
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(".env.noticias")

from modules.pesquisa import gerar_resumo_completo
from modules.notebooklm import executar_fluxo_notebooklm
from modules.telegram_sender import (
    enviar_audio_telegram,
    enviar_notificacao_erro,
    enviar_notificacao_inicio,
)

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(f"logs/noticias_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def executar_pipeline_noticias():
    # Impede o Mac de dormir durante a execução
    cafeinado = subprocess.Popen(["caffeinate", "-i"])

    inicio = datetime.now()
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO PIPELINE DE NOTÍCIAS DE TECNOLOGIA")
    logger.info(f"⏰ {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)

    data_str = inicio.strftime("%d/%m/%Y")
    enviar_notificacao_inicio()

    try:
        logger.info("\n📰 ETAPA 1: Pesquisando notícias de tecnologia...")
        resumo, caminho_resumo = gerar_resumo_completo()
        logger.info(f"✅ Resumo gerado: {len(resumo)} caracteres")

        logger.info("\n🤖 ETAPA 2-4: Automação do NotebookLM...")
        caminho_audio = executar_fluxo_notebooklm(caminho_resumo)

        if not caminho_audio:
            raise Exception("Não foi possível obter o áudio")

        logger.info("\n📱 ETAPA 5: Enviando pelo Telegram...")
        sucesso = enviar_audio_telegram(caminho_audio, data_str)

        if sucesso:
            duracao = (datetime.now() - inicio).seconds // 60
            logger.info(f"\n🎉 PIPELINE DE NOTÍCIAS CONCLUÍDO em {duracao} minutos!")
        else:
            raise Exception("Falha ao enviar pelo Telegram")

    except Exception as e:
        logger.error(f"\n❌ ERRO: {e}")
        enviar_notificacao_erro(str(e))

    finally:
        cafeinado.terminate()
        logger.info("☕ Caffeinate encerrado")


def main():
    horario = os.getenv("SCHEDULE_TIME", "05:40")
    logger.info(f"⏰ Agendando notícias diárias às {horario}")

    schedule.every().day.at(horario).do(executar_pipeline_noticias)

    import sys
    if "--agora" in sys.argv:
        logger.info("🚀 Execução imediata!")
        executar_pipeline_noticias()
        return

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()