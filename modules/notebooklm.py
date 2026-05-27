import os
import time
import shutil
import subprocess
import logging
from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

from modules.visao_selenium import passo_inteligente, verificar_audio_pronto


load_dotenv()
logger = logging.getLogger(__name__)

NOTEBOOKLM_URL = "https://notebooklm.google.com"
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL_MINUTES", "15")) * 60
MAX_TENTATIVAS_POLLING = int(os.getenv("MAX_POLLING_ATTEMPTS", "8"))

def configurar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--force-device-scale-factor=1")  # <- adiciona essa linha
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--user-data-dir=/Users/guilherme/chrome-bot-profile")
    options.add_argument("--profile-directory=Default")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def criar_projeto_notebooklm(driver):
    logger.info("Abrindo NotebookLM...")
    driver.get(NOTEBOOKLM_URL)
    time.sleep(8)

    # Clica direto pelo texto do botão usando JavaScript
    try:
        botao = driver.find_element(By.XPATH, "//*[contains(text(), 'Criar novo')]")
        driver.execute_script("arguments[0].click();", botao)
        logger.info("Clicou em Criar novo!")
        time.sleep(3)
        return True
    except Exception as e:
        logger.error(f"Erro ao clicar em Criar novo: {e}")
        return False



def fazer_upload_resumo(driver, caminho_arquivo):
    logger.info("Colando resumo via Texto copiado...")

    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Clica em Texto copiado
    try:
        botao = driver.find_element(By.XPATH, "//*[contains(text(), 'Texto copiado')]")
        driver.execute_script("arguments[0].click();", botao)
        logger.info("Clicou em Texto copiado!")
        time.sleep(3)
    except Exception as e:
        logger.error(f"Erro ao clicar em Texto copiado: {e}")
        return False

    # Cola o conteúdo diretamente via JavaScript no textarea do modal
    try:
        textarea = driver.find_element(By.XPATH, "//textarea[contains(@placeholder, 'Cole') or contains(@placeholder, 'texto')]")
        driver.execute_script("arguments[0].value = arguments[1];", textarea, conteudo)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", textarea)
        logger.info("Conteúdo colado via JavaScript!")
        time.sleep(2)
    except Exception as e:
        logger.error(f"Erro ao colar conteúdo: {e}")
        return False

    # Clica em Inserir
    try:
        botao_inserir = driver.find_element(By.XPATH, "//*[contains(text(), 'Inserir')]")
        driver.execute_script("arguments[0].click();", botao_inserir)
        logger.info("Clicou em Inserir!")
        time.sleep(5)
    except Exception as e:
        logger.error(f"Erro ao clicar em Inserir: {e}")
        return False

    return True


def gerar_audio(driver):
    logger.info("Aguardando 2 minutos antes de gerar áudio...")
    time.sleep(120)

    logger.info("Clicando em Resumo em Audio...")
    try:
        botao = driver.find_element(By.XPATH, "//*[contains(text(), 'Resumo em')]")
        driver.execute_script("arguments[0].click();", botao)
        logger.info("Clicou em Resumo em Audio!")
        time.sleep(3)
    except Exception as e:
        logger.error(f"Erro ao clicar em Resumo em Audio: {e}")
        return False

    # Confirma se aparecer botão Generate
    try:
        botao_gerar = driver.find_element(By.XPATH, "//*[contains(text(), 'Gerar') or contains(text(), 'Generate')]")
        driver.execute_script("arguments[0].click();", botao_gerar)
        logger.info("Confirmou geração!")
    except Exception:
        pass

    return True


def aguardar_e_baixar_audio(driver, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    url_notebook = driver.current_url
    logger.info(f"URL do notebook: {url_notebook}")
    logger.info("Aguardando 18 minutos para o audio ser gerado...")
    time.sleep(1080)

    intervalo_checagem = 3 * 60
    max_checagens = 3

    for tentativa in range(max_checagens + 1):
        logger.info(f"Verificacao {tentativa+1}/{max_checagens+1}")

        driver.get(url_notebook)
        time.sleep(8)
        driver.save_screenshot(f"logs/verificacao_{tentativa+1}.png")

        try:
            # Verifica se existe botão de PLAY no card de audio
            # Isso confirma que o audio está PRONTO, não gerando
            play = driver.find_element(By.XPATH, 
                "//button[contains(@aria-label,'Play') or contains(@aria-label,'Reproduzir')] | "
                "//*[contains(@class,'play-button')] | "
                "//mat-icon[text()='play_arrow']/parent::button"
            )
            logger.info("Audio PRONTO — botão play encontrado!")
            return baixar_audio(driver, output_dir)

        except Exception:
            # Verifica se ainda está gerando
            try:
                gerando = driver.find_element(By.XPATH, 
                    "//*[contains(text(),'Gerando') or contains(text(),'Volte em') or contains(text(),'gerando')]"
                )
                logger.info(f"Audio ainda gerando. Verificando em 3 minutos...")
            except Exception:
                logger.info(f"Status desconhecido. Verificando em 3 minutos...")

            if tentativa < max_checagens:
                time.sleep(intervalo_checagem)
            else:
                logger.error("Timeout: audio nao ficou pronto")

    return None


def baixar_audio(driver, output_dir):
    nome_arquivo = f"podcast_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        # Salva print para debug
        driver.save_screenshot("logs/antes_download.png")
        
        botoes = driver.find_elements(By.XPATH, "//mat-icon[text()='more_vert']/parent::button")
        logger.info(f"Encontrou {len(botoes)} botoes more_vert")
        botoes[-1].click()
        time.sleep(5)

        # Salva print após clicar nos 3 pontinhos
        driver.save_screenshot("logs/apos_3_pontinhos.png")

        wait = WebDriverWait(driver, 15)
        baixar = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(text(),'Baixar')]")
        ))
        momento_download = time.time()
        driver.execute_script("arguments[0].click();", baixar)
        logger.info("Clicou em Baixar!")
        time.sleep(15)

        downloads_dir = Path.home() / "Downloads"
        arquivos = (
            list(downloads_dir.glob("*.wav")) +
            list(downloads_dir.glob("*.mp3")) +
            list(downloads_dir.glob("*.aac")) +
            list(downloads_dir.glob("*.m4a"))
        )
        arquivos_novos = [f for f in arquivos if f.stat().st_mtime > momento_download]

        if not arquivos_novos:
            logger.error("Nenhum arquivo novo encontrado em Downloads!")
            return None

        mais_recente = max(arquivos_novos, key=lambda p: p.stat().st_mtime)
        tamanho_mb = mais_recente.stat().st_size / (1024 * 1024)
        logger.info(f"Arquivo baixado: {mais_recente.name} ({tamanho_mb:.1f} MB)")

        arquivo_comprimido = Path(output_dir) / f"{nome_arquivo}.mp3"
        logger.info("Comprimindo audio...")
        subprocess.run([
            "/opt/homebrew/bin/ffmpeg", "-y",
            "-i", str(mais_recente),
            "-b:a", "64k",
            "-ar", "44100",
            str(arquivo_comprimido)
        ], capture_output=True)

        tamanho_final = arquivo_comprimido.stat().st_size / (1024 * 1024)
        logger.info(f"Comprimido: {tamanho_final:.1f} MB")
        return str(arquivo_comprimido)

    except Exception as e:
        logger.error(f"Erro ao baixar audio: {e}")
        driver.save_screenshot("logs/erro_download.png")
        return None

def executar_fluxo_notebooklm(caminho_resumo):
    driver = configurar_driver()
    try:
        if not criar_projeto_notebooklm(driver):
            raise Exception("Falha ao criar projeto")
        if not fazer_upload_resumo(driver, caminho_resumo):
            raise Exception("Falha no upload")
        if not gerar_audio(driver):
            raise Exception("Falha ao gerar audio")
        audio = aguardar_e_baixar_audio(driver)
        if not audio:
            raise Exception("Falha ao baixar audio")
        return audio
    except Exception as e:
        logger.error(f"Erro: {e}")
        try:
            driver.save_screenshot("logs/erro_notebooklm.png")
        except:
            pass
        return None
    finally:
        driver.quit()

