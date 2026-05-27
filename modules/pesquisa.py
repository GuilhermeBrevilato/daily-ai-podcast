"""
Módulo 1: Agente de Pesquisa
- Busca os 10 principais estudos de IA e 10 notícias de tecnologia
- Resume cada resultado usando GPT-4o
"""

import os
import json
import logging
from datetime import datetime
from ddgs import DDGS
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def buscar_artigos(topico: str, max_results: int = 10) -> list[dict]:
    """Busca artigos no DuckDuckGo sobre o tópico dado."""
    logger.info(f"Buscando: {topico}")
    resultados = []

    with DDGS() as ddgs:
        for r in ddgs.news(topico, max_results=max_results):
            resultados.append({
                "titulo": r.get("title", ""),
                "url": r.get("url", ""),
                "fonte": r.get("source", ""),
                "data": r.get("date", ""),
                "resumo_bruto": r.get("body", ""),
            })

    logger.info(f"Encontrados {len(resultados)} artigos para '{topico}'")
    return resultados


def resumir_artigos(artigos: list[dict], topico: str) -> str:
    if not artigos:
        return f"Nenhum artigo encontrado para: {topico}"

    lista_artigos = "\n\n".join([
        f"[{i+1}] {a['titulo']}\nFonte: {a['fonte']} | Data: {a['data']}\n{a['resumo_bruto']}"
        for i, a in enumerate(artigos)
    ])

    prompt = f"""Você é um curador de conteúdo especializado em tecnologia e inteligência artificial.

Abaixo estão os principais artigos sobre: "{topico}"

{lista_artigos}

Produza um briefing rico e provocativo (1500 a 2000 palavras) otimizado para ser usado no NotebookLM e gerar um podcast de alta qualidade. O texto deve ser escrito de forma que dois apresentadores consigam debater, questionar e se surpreender com o conteúdo.

Estruture assim:

## {topico.upper()} — Briefing do Dia

### O Panorama Atual
Escreva 2-3 parágrafos contextualizando o momento atual deste tema. Por que está acontecendo agora? Quais forças — econômicas, tecnológicas ou sociais — estão impulsionando isso? Apresente o cenário de forma que qualquer pessoa consiga entender a importância do que está acontecendo.

### Os Destaques que Você Precisa Conhecer

Para cada um dos 5 artigos mais relevantes:

**[Número]. [Título]**
*Fonte: [fonte] | [data]*

O que aconteceu: [2-3 frases diretas explicando o fato]

Por que isso importa agora: [2-3 frases sobre o impacto real — no mercado, na ciência, no dia a dia das pessoas]

Aplicação prática: [Como isso pode ser usado, aproveitado ou do que se proteger — seja por empresas, desenvolvedores ou pessoas comuns]

Tensão ou controvérsia: [Existe algum lado negativo, risco, crítica ou visão oposta? Se sim, apresente com clareza]

Pergunta para reflexão: [Uma pergunta aberta e provocativa que os apresentadores podem debater — ex: "Mas será que isso vai realmente democratizar o acesso ou vai concentrar ainda mais poder nas mãos de poucos?"]

### O Que Está em Tensão
Escreva 2-3 parágrafos identificando as contradições e conflitos centrais do tema. Onde há discordância entre especialistas? O que parece promissor mas tem riscos escondidos? O que a mídia mainstream está ignorando?

### Aplicabilidade Real — O Que Você Pode Fazer com Isso
Liste 4-5 insights concretos e acionáveis. Para cada um, indique se é relevante para: desenvolvedores, empresas, investidores ou o público geral.

### As Perguntas que Ficam no Ar
Liste 3-4 perguntas abertas e instigantes sobre o futuro deste tema. Essas perguntas devem ser boas o suficiente para gerar debate genuíno entre os apresentadores do podcast.

### Frase do Dia
Uma frase impactante — pode ser uma citação real de algum dos artigos ou uma síntese sua — que capture a essência do momento atual deste tema.
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.7,
    )

    return response.choices[0].message.content

def gerar_resumo_completo() -> str:
    """
    Função principal: pesquisa todos os tópicos e gera o resumo completo
    que será enviado ao NotebookLM.
    """
    topicos_raw = os.getenv("RESEARCH_TOPICS", "agentes de inteligência artificial|notícias de tecnologia")
    topicos = [t.strip() for t in topicos_raw.split("|")]
    max_results = int(os.getenv("RESULTS_PER_TOPIC", "10"))

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    secoes = [f"# Briefing Diário de IA e Tecnologia\n**Data:** {data_hoje}\n"]

    for topico in topicos:
        try:
            artigos = buscar_artigos(topico, max_results)
            resumo = resumir_artigos(artigos, topico)
            secoes.append(resumo)
            logger.info(f"✅ Tópico concluído: {topico}")
        except Exception as e:
            logger.error(f"❌ Erro ao processar '{topico}': {e}")
            secoes.append(f"## {topico.upper()}\n\nErro ao buscar dados: {e}")

    resumo_final = "\n\n---\n\n".join(secoes)

    # Salva o resumo em arquivo para uso posterior
    output_path = f"output/resumo_{datetime.now().strftime('%Y%m%d')}.txt"
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(resumo_final)

    logger.info(f"📄 Resumo salvo em: {output_path}")
    return resumo_final, output_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    resumo, caminho = gerar_resumo_completo()
    print(resumo)
    print(f"\n✅ Salvo em: {caminho}")
