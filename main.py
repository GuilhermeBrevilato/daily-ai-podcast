"""
🎙️ Daily AI Podcast - Orquestrador Principal
"""

import os
import time
import logging
import schedule
import subprocess
from datetime import datetime
from dotenv import load_dotenv

from modules.pesquisa import gerar_resumo_completo
from modules.notebooklm import executar_fluxo_notebooklm
from modules.telegram_sender import (
    enviar_audio_telegram,
    enviar_notificacao_erro,
    enviar_notificacao_inicio,
)

load_dotenv()

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(f"logs/podcast_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)


def executar_pipeline():
    # Impede o Mac de dormir durante a execução
    cafeinado = subprocess.Popen(["caffeinate", "-i"])

    inicio = datetime.now()
    logger.info("=" * 60)
    logger.info("🚀 INICIANDO PIPELINE DO PODCAST DIÁRIO")
    logger.info(f"⏰ {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)

    data_str = inicio.strftime("%d/%m/%Y")
    enviar_notificacao_inicio()

    try:
        logger.info("\n📰 ETAPA 1: Pesquisando e resumindo conteúdo...")
        resumo, caminho_resumo = gerar_resumo_completo()
        logger.info(f"✅ Resumo gerado: {len(resumo)} caracteres")

        logger.info("\n🤖 ETAPA 2-4: Automação do NotebookLM...")
        caminho_audio = executar_fluxo_notebooklm(caminho_resumo)

        if not caminho_audio:
            raise Exception("Não foi possível obter o áudio do NotebookLM")

        logger.info("\n📱 ETAPA 5: Enviando pelo Telegram...")
        sucesso = enviar_audio_telegram(caminho_audio, data_str)

        if sucesso:
            duracao = (datetime.now() - inicio).seconds // 60
            logger.info(f"\n🎉 PIPELINE CONCLUÍDO com sucesso em {duracao} minutos!")
        else:
            raise Exception("Falha ao enviar pelo Telegram")

    except Exception as e:
        logger.error(f"\n❌ ERRO NO PIPELINE: {e}")
        enviar_notificacao_erro(str(e))

    finally:
        cafeinado.terminate()
        logger.info("☕ Caffeinate encerrado")


def main():
    horario = os.getenv("SCHEDULE_TIME", "06:00")

    logger.info(f"⏰ Agendando execução diária às {horario}")
    logger.info("💡 Para testar agora, execute: python main.py --agora")

    schedule.every().day.at(horario).do(executar_pipeline)

    import sys
    if "--agora" in sys.argv:
        logger.info("🚀 Execução imediata solicitada!")
        executar_pipeline()
        return

    logger.info(f"✅ Scheduler ativo. Próxima execução às {horario}")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()