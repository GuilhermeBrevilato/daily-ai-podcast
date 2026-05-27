"""
Módulo 2: Agente de Visão + Selenium
- Tira print da tela
- GPT-4o analisa o print e retorna o seletor/coordenada do elemento
- Selenium executa a ação
- Loop adaptativo: cada passo gera novo código baseado no novo estado da tela
"""

import os
import time
import base64
import logging
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def configurar_driver() -> webdriver.Chrome:
    """Configura e retorna o driver do Chrome."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Descomente para rodar sem janela
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    return driver


def tirar_print(driver: webdriver.Chrome) -> tuple[bytes, str]:
    """Tira print da tela atual e retorna bytes + base64."""
    screenshot_bytes = driver.get_screenshot_as_png()
    screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
    return screenshot_bytes, screenshot_b64


def analisar_tela_com_ia(screenshot_b64: str, instrucao: str) -> dict:
    """
    Envia o print para o GPT-4o Vision e pede que identifique
    o elemento correto e retorne o seletor ou coordenada.
    """
    prompt = f"""Você é um especialista em automação web. Analise esta captura de tela do NotebookLM.

TAREFA: {instrucao}

Responda APENAS em JSON válido, sem markdown, no seguinte formato:
{{
  "encontrado": true/false,
  "tipo_acao": "click" | "upload" | "type" | "wait",
  "metodo": "xpath" | "css" | "coordenada",
  "seletor": "valor do seletor ou null",
  "coordenada_x": numero_ou_null,
  "coordenada_y": numero_ou_null,
  "texto_para_digitar": "texto_ou_null",
  "descricao": "descrição do que foi encontrado",
  "confianca": "alta" | "media" | "baixa"
}}

Prefira XPath ou CSS selector. Use coordenadas apenas como último recurso.
Se não encontrar o elemento, coloque encontrado: false."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}",
                            "detail": "high"
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        max_tokens=500,
        temperature=0.1,
    )

    raw = response.choices[0].message.content.strip()
    
    # Remove possíveis markdown fences
    raw = raw.replace("```json", "").replace("```", "").strip()
    
    import json
    resultado = json.loads(raw)
    logger.info(f"IA identificou: {resultado.get('descricao')} (confiança: {resultado.get('confianca')})")
    return resultado


def executar_acao(driver: webdriver.Chrome, acao: dict) -> bool:
    """Executa a ação identificada pela IA."""
    if not acao.get("encontrado"):
        logger.warning("Elemento não encontrado pela IA")
        return False

    tipo = acao.get("tipo_acao")
    metodo = acao.get("metodo")
    seletor = acao.get("seletor")

    try:
        if metodo == "xpath" and seletor:
            elemento = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, seletor))
            )
        elif metodo == "css" and seletor:
            elemento = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, seletor))
            )
        elif metodo == "coordenada":
            x = acao.get("coordenada_x")
            y = acao.get("coordenada_y")
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).move_by_offset(x, y).click().perform()
            logger.info(f"Clicou na coordenada ({x}, {y})")
            return True
        else:
            logger.error(f"Método desconhecido: {metodo}")
            return False

        if tipo == "click":
            elemento.click()
            logger.info(f"✅ Clicou em: {acao.get('descricao')}")
        elif tipo == "type":
            texto = acao.get("texto_para_digitar", "")
            elemento.clear()
            elemento.send_keys(texto)
            logger.info(f"✅ Digitou texto em: {acao.get('descricao')}")
        elif tipo == "upload":
            arquivo = acao.get("texto_para_digitar", "")
            elemento.send_keys(arquivo)
            logger.info(f"✅ Upload do arquivo: {arquivo}")

        return True

    except Exception as e:
        logger.error(f"❌ Erro ao executar ação: {e}")
        return False


def passo_inteligente(driver: webdriver.Chrome, instrucao: str, max_tentativas: int = 3) -> bool:
    """
    Executa um passo completo:
    1. Tira print
    2. IA analisa e decide ação
    3. Selenium executa
    4. Retry se necessário
    """
    for tentativa in range(max_tentativas):
        logger.info(f"Passo '{instrucao}' - tentativa {tentativa + 1}/{max_tentativas}")
        
        time.sleep(2)  # Aguarda a página estabilizar
        _, screenshot_b64 = tirar_print(driver)
        
        acao = analisar_tela_com_ia(screenshot_b64, instrucao)
        
        if acao.get("confianca") == "baixa" and tentativa < max_tentativas - 1:
            logger.warning("Confiança baixa, aguardando e tentando novamente...")
            time.sleep(3)
            continue
        
        sucesso = executar_acao(driver, acao)
        if sucesso:
            time.sleep(2)
            return True
    
    logger.error(f"❌ Falha após {max_tentativas} tentativas: {instrucao}")
    return False


def verificar_audio_pronto(driver: webdriver.Chrome) -> str:
    """
    Verifica o estado do áudio na página.
    Retorna: 'pronto' | 'gerando' | 'erro' | 'nao_encontrado'
    """
    _, screenshot_b64 = tirar_print(driver)

    prompt = """Analise esta tela do NotebookLM e identifique o status do áudio.

Responda APENAS em JSON:
{
  "status": "pronto" | "gerando" | "erro" | "nao_encontrado",
  "descricao": "o que você viu na tela",
  "botao_download_xpath": "xpath do botão de download se encontrado, ou null"
}

- "pronto": há um botão de download ou play do áudio disponível
- "gerando": há algum indicador de carregamento/processamento do áudio
- "erro": há mensagem de erro
- "nao_encontrado": não foi possível identificar o status"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_b64}",
                            "detail": "high"
                        }
                    },
                    {"type": "text", "text": prompt}
                ]
            }
        ],
        max_tokens=300,
        temperature=0.1,
    )

    import json
    raw = response.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
    resultado = json.loads(raw)
    logger.info(f"Status do áudio: {resultado['status']} - {resultado['descricao']}")
    return resultado
