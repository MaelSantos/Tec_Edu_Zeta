import json
import logging
import re
import concurrent.futures
from typing import List, Optional, Union

import httpx
from bs4 import BeautifulSoup

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.postgres import PostgresDb
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools
from agno.tools.valyu import ValyuTools
from dotenv import load_dotenv
from fastapi import HTTPException, status

from api.schemas.chat_schema import (
    AvaliacaoResponse,
    QuizResponse,
    ResumoResponse,
    RevisaoResponse,
)
from api.utils import constants
from api.utils.enums import TipoAcao
from api.utils.instructions import AGENT_INSTRUCTIONS, gerar_contexto_agente

logger = logging.getLogger(__name__)

load_dotenv()


MODE_SCHEMAS = {
    "Resumo": ResumoResponse,
    "Exercício": AvaliacaoResponse,
    "Revisão": RevisaoResponse,
    "Quiz": QuizResponse,
}

NUM_PREDICT_POR_MODO = {
    "Resumo": 512,
    "Exercício": 900,
    "Quiz": 900,
    "Revisão": 700,
}

VISUAL_POR_MODO = {
    "Resumo": (
    "No campo 'visual', inclua sempre um mapa mental no campo 'mindmap' "
    "(markdown com # headings), resumindo os pontos principais do assunto."
    ),
    "Exercício": (
    "No campo 'visual', deixe todos os subcampos como null. "
    "As proprias questoes com alternativas ja cumprem o papel de conteudo estruturado."
    ),
    "Revisão": (
    "No campo 'visual', inclua sempre flashcards no campo 'flashcards' "
    "(lista de pares pergunta/resposta), um para cada item do cronograma."
    ),
    "Quiz": (
    "No campo 'visual', deixe todos os subcampos como null. "
    "As proprias perguntas do quiz ja cumprem o papel de conteudo estruturado."
    ),
}

import re as _re

_TEMAS_SENSIVEIS_ = [
    {
        "nome": "suicidio",
        "regex": _re.compile(
            r"\b(?:quero|vou|pretendo) morrer\b(?! de )|"
            r"\bmorrer (?:amanh[ãa]|hoje|agora)\b|"
            r"\btirar a (?:pr[óo]pria )?vida\b|"
            r"\bacabar com (?:a vida|tudo)\b|"
            r"\b(?:se |me )?matar\b(?! (?:de |aula?\b))|"
            r"\bautomutilação\b|"
            r"\bself[- ]?harm\b|"
            r"\b(?:me |se )?cort[áa]r\b(?! (?:de |aula?\b))|"
            r"\b(?:me |se )?machucar\b(?! (?:de |aula?\b))",
            _re.IGNORECASE
        ),
        "titulo": "Precisando de ajuda?",
        "mensagem": (
            "Percebi que voc\u00ea pode estar passando por um momento dif\u00edcil. "
            "Saiba que n\u00e3o precisa enfrentar isso sozinho(a). "
            "O Centro de Valoriza\u00e7\u00e3o da Vida (CVV) oferece apoio emocional "
            "gratuito e sigiloso, 24 horas por dia, pelo telefone 188 "
            "ou pelo site www.cvv.org.br. "
            "Converse com algu\u00e9m de confian\u00e7a ou procure um profissional de sa\u00fade. "
            "Se quiser, podemos conversar sobre outro assunto escolar."
        ),
        "sugestoes": [
            "Ligue 188 (CVV) - Atendimento 24h",
            "Converse com algu\u00e9m de confian\u00e7a",
            "O que voc\u00ea gostaria de estudar hoje?",
        ],
        "_debug": "Palavras-chave de suic\u00eddio ou automutila\u00e7\u00e3o detectadas.",
    },
    {
        "nome": "depressao",
        "regex": _re.compile(
            r"\bestou (?:deprimid[oa]|com depress[aã]o)\b|"
            r"\b(?:diagnosticad[oa]|sofro) (?:com |de )?(?:depress[aã]o)\b|"
            r"\bn[aã]o (?:tenho|sinto) (?:mais )?vontade de (?:viver|continuar|fazer nada)\b",
            _re.IGNORECASE
        ),
        "titulo": "Voc\u00ea n\u00e3o est\u00e1 sozinho(a)",
        "mensagem": (
            "Percebi que voc\u00ea pode estar passando por um per\u00edodo dif\u00edcil com a depress\u00e3o. "
            "Saiba que isso \u00e9 uma condi\u00e7\u00e3o de sa\u00fade e voc\u00ea n\u00e3o precisa enfrentar sozinho(a). "
            "Converse com seus pais ou respons\u00e1veis sobre como est\u00e1 se sentindo. "
            "O CVV oferece apoio emocional gratuito pelo telefone 188, 24 horas por dia. "
            "Procure tamb\u00e9m um profissional de sa\u00fade para receber o acompanhamento adequado."
        ),
        "sugestoes": [
            "Ligue 188 (CVV) - Apoio emocional 24h",
            "Converse com seus pais ou respons\u00e1veis",
            "Procure um profissional de sa\u00fade",
        ],
        "_debug": "Palavras-chave de depress\u00e3o detectadas.",
    },
    {
        "nome": "ansiedade",
        "regex": _re.compile(
            r"\bestou (?:ansios[oa]|com ansiedade|muito nervos[oa])\b|"
            r"\b(?:crise de ansiedade|ataque de p[aâ]nico)\b|"
            r"\b(?:sofro|tenho) (?:de |com )?ansiedade\b",
            _re.IGNORECASE
        ),
        "titulo": "Respire fundo",
        "mensagem": (
            "Percebi que voc\u00ea pode estar se sentindo ansioso(a). "
            "Tente respirar fundo algumas vezes: inspire por 4 segundos, "
            "segure por 4, expire por 4. "
            "Se a ansiedade for frequente, converse com seus pais ou respons\u00e1veis "
            "e procure um profissional de sa\u00fade. "
            "O CVV tamb\u00e9m oferece apoio pelo telefone 188."
        ),
        "sugestoes": [
            "Respire fundo: inspire 4s, segure 4s, expire 4s",
            "Converse com algu\u00e9m de confian\u00e7a",
            "Procure um profissional de sa\u00fade",
        ],
        "_debug": "Palavras-chave de ansiedade detectadas.",
    },
    {
        "nome": "abuso",
        "regex": _re.compile(
            r"\b(?:abus[ao] sexual|estupro|assed[io] sexual)\b|"
            r"\bviol[eê]ncia dom[ée]stica\b|"
            r"\b(?:sofro|sofri) (?:abuso|viol[eê]ncia)\b|"
            r"\b(?:fui|estou sendo) (?:abusad[ao]|violentad[ao])\b",
            _re.IGNORECASE
        ),
        "titulo": "Voc\u00ea merece prote\u00e7\u00e3o",
        "mensagem": (
            "Sinto muito que voc\u00ea esteja passando por isso. "
            "Ningu\u00e9m merece sofrer viol\u00eancia ou abuso. "
            "Voc\u00ea pode denunciar ligando para o Disque 100, que \u00e9 gratuito e sigiloso. "
            "Converse com um adulto de confian\u00e7a, como seus pais, um professor "
            "ou o conselheiro escolar. Voc\u00ea n\u00e3o est\u00e1 sozinho(a)."
        ),
        "sugestoes": [
            "Disque 100 - Den\u00fancia sigilosa",
            "Converse com um adulto de confian\u00e7a",
            "Procure ajuda de um profissional",
        ],
        "_debug": "Palavras-chave de abuso ou viol\u00eancia detectadas.",
    },
    {
        "nome": "bullying",
        "regex": _re.compile(
            r"\b(?:sofro|sofrendo) bullying\b|"
            r"\b(?:estou sendo|sou) (?:bullying|perseguid[oa]|humilhad[oa])\b|"
            r"\b(?:meus colegas|meus amigos) (?:me )?(?:humilham|zoam|maltratam)\b|"
            r"\bn[aã]o (?:quero|gosto de) ir (?:para |na )?escola (?:por causa|por conta) (?:de |do )?(?:bullying|humilhação|zoação)\b",
            _re.IGNORECASE
        ),
        "titulo": "Bullying n\u00e3o \u00e9 brincadeira",
        "mensagem": (
            "Sinto muito que voc\u00ea esteja passando por bullying. "
            "Saiba que isso n\u00e3o \u00e9 sua culpa e voc\u00ea n\u00e3o precisa aceitar isso. "
            "Converse com seus pais, um professor ou o diretor da escola. "
            "Voc\u00ea tamb\u00e9m pode ligar para o Disque 100 e pedir orienta\u00e7\u00e3o. "
            "N\u00e3o fique calado(a) - pedir ajuda \u00e9 o primeiro passo."
        ),
        "sugestoes": [
            "Converse com seus pais ou respons\u00e1veis",
            "Fale com um professor ou diretor",
            "Disque 100 - Orientação e denúncia",
        ],
        "_debug": "Palavras-chave de bullying detectadas.",
    },
    {
        "nome": "luto",
        "regex": _re.compile(
            r"\b(?:perdi|perdeu|morreu|faleceu) (?:meu|minha|um)\b|"
            r"\bestou de luto\b|"
            r"\b(?:meu|minha) (?:mãe|pai|avô|avó|irmão|irmã|amigo) morreu\b|"
            r"\bn[aã]o (?:consigo|sei) lidar com (?:a perda|o luto|a morte)\b",
            _re.IGNORECASE
        ),
        "titulo": "Meus sentimentos",
        "mensagem": (
            "Sinto muito pela sua perda. Passar pelo luto \u00e9 dif\u00edcil "
            "e cada pessoa vive isso de um jeito. "
            "N\u00e3o tenha medo de falar sobre o que est\u00e1 sentindo com "
            "pessoas de confian\u00e7a. Se precisar de apoio, o CVV oferece "
            "acolhimento gratuito pelo telefone 188."
        ),
        "sugestoes": [
            "Converse com algu\u00e9m de confian\u00e7a sobre seus sentimentos",
            "Ligue 188 (CVV) - Apoio emocional",
            "Escreva ou desenhe como est\u00e1 se sentindo",
        ],
        "_debug": "Palavras-chave de luto detectadas.",
    },
    {
        "nome": "familia",
        "regex": _re.compile(
            r"\b(?:minha|meu) (?:m[aã]e|pai|fam[ií]lia|irm[ãa]o|irm[ãa]|av[óo]) (?:precisa|est[áa] (?:doente|morrendo|passando mal|mal)|morreu|salva[cç][aã]o)\b|"
            r"\b(?:problemas|brigas|discussões) (?:em casa|na fam[ií]lia|com meus pais)\b|"
            r"\b(?:meus pais) (?:est[ãa]o (?:se separando|brigando|divorciando))\b",
            _re.IGNORECASE
        ),
        "titulo": "Como posso ajudar?",
        "mensagem": (
            "Percebi que voc\u00ea pode estar passando por uma situa\u00e7\u00e3o dif\u00edcil em fam\u00edlia. "
            "Converse com um adulto de confian\u00e7a sobre o que est\u00e1 acontecendo. "
            "Se precisar de apoio, o CVV oferece acolhimento gratuito pelo telefone 188. "
            "Lembre-se de que voc\u00ea n\u00e3o \u00e9 respons\u00e1vel pelos problemas dos adultos."
        ),
        "sugestoes": [
            "Converse com um adulto de confian\u00e7a",
            "Ligue 188 (CVV) - Apoio emocional",
            "Quer conversar sobre algum assunto escolar?",
        ],
        "_debug": "Palavras-chave de problemas familiares detectadas.",
    },
    {
        "nome": "saude",
        "regex": _re.compile(
            r"\b(?:estou|t[áa]?) (?:doente|com febre|passando mal|me sentindo mal|mal)\b|"
            r"\b(?:preciso|precisa) (?:de um m[eé]dico|ir ao hospital|de ajuda m[eé]dica)\b|"
            r"\b(?:não sei|nao sei) o que fazer\b",
            _re.IGNORECASE
        ),
        "titulo": "Cuide da sua sa\u00fade",
        "mensagem": (
            "Se voc\u00ea n\u00e3o est\u00e1 se sentindo bem, o mais importante \u00e9 "
            "contar para um adulto de confian\u00e7a: seus pais, respons\u00e1veis "
            "ou um professor. Eles podem te ajudar a procurar atendimento m\u00e9dico "
            "se necess\u00e1rio. N\u00e3o fique sofrendo sozinho(a)."
        ),
        "sugestoes": [
            "Converse com seus pais ou respons\u00e1veis",
            "Procure um posto de sa\u00fade ou hospital",
            "Quer estudar algum assunto escolar?",
        ],
        "_debug": "Palavras-chave de sa\u00fade detectadas.",
    },
]

_PADRAO_INAPROPRIADO_ = _re.compile(
    r"\b(?:fugir|matar|pular|cabular) (?:da |de |a )?(?:escola|aula)\b|"
    r"\bcolar na prova\b|"
    r"\b(?:como )?(?:roubar|enganar|falsificar|trapacear)\b|"
    r"\bwifi gr[áa]tis na escola\b|"
    r"\b(?:como )?fazer (?:armas?|bombas?)\b",
    _re.IGNORECASE
)

def web_search(query: str, max_results: int = 5) -> dict:
    """Search the web via DuckDuckGo HTML endpoint, fallback to Wikipedia.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.

    Returns:
        Dict with 'source' and 'results' keys.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
    }
    results = []
    source = ""

    # 1) Try DuckDuckGo HTML endpoint directly
    try:
        with httpx.Client(timeout=8, verify=False) as client:
            resp = client.post(
                "https://html.duckduckgo.com/html/",
                data={"q": query},
                headers=headers,
            )
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for i, item in enumerate(soup.select(".result")):
                if i >= max_results:
                    break
                title_el = item.select_one(".result__title a")
                snippet_el = item.select_one(".result__snippet")
                url_el = item.select_one(".result__url")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "href": title_el.get("href", ""),
                        "body": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            if results:
                source = "DuckDuckGo"
    except Exception:
        pass

    # 2) Fallback: Wikipedia API
    if not results:
        try:
            with httpx.Client(timeout=8, verify=False) as client:
                wiki_resp = client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "opensearch",
                        "search": query,
                        "limit": max_results,
                        "namespace": 0,
                        "format": "json",
                    },
                )
            if wiki_resp.status_code == 200:
                data = wiki_resp.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                for i, title in enumerate(titles):
                    results.append({
                        "title": title,
                        "href": urls[i] if i < len(urls) else "",
                        "body": "",
                    })
                if results:
                    source = "Wikipedia (EN)"
        except Exception:
            pass

    # 3) Last resort: Wikipedia PT
    if not results:
        try:
            with httpx.Client(timeout=8, verify=False) as client:
                wiki_resp = client.get(
                    "https://pt.wikipedia.org/w/api.php",
                    params={
                        "action": "opensearch",
                        "search": query,
                        "limit": max_results,
                        "namespace": 0,
                        "format": "json",
                    },
                )
            if wiki_resp.status_code == 200:
                data = wiki_resp.json()
                titles = data[1] if len(data) > 1 else []
                urls = data[3] if len(data) > 3 else []
                for i, title in enumerate(titles):
                    results.append({
                        "title": title,
                        "href": urls[i] if i < len(urls) else "",
                        "body": "",
                    })
                if results:
                    source = "Wikipedia (PT)"
        except Exception:
            pass

    return {"source": source, "results": results}


def _verificar_tema_sensivel(texto: str) -> dict | None:
    for tema in _TEMAS_SENSIVEIS_:
        if tema["regex"].search(texto):
            return {
                "tipo": "resumo",
                "titulo": tema["titulo"],
                "resumo": tema["mensagem"],
                "sugestoes": tema["sugestoes"][:],
                "visual": None,
                "_debug": [{"tipo": "bloqueio", "conteudo": tema["_debug"]}],
            }
    return None


def _extrair_json(texto: str) -> dict | None:
    if not texto:
        return None
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _gerar_descricao_schema(schema) -> str:
    props = []
    for nome, campo in schema.model_fields.items():
        tipo = "string"
        annotation = campo.annotation

        def _unwrap(ann):
            if hasattr(ann, "__origin__"):
                if ann.__origin__ is Union:
                    args = ann.__args__
                    non_none = [a for a in args if a is not None.__class__]
                    if non_none:
                        return _unwrap(non_none[0])
                elif ann.__origin__ is list:
                    item = ann.__args__[0]
                    nome_item = item.__name__ if hasattr(item, "__name__") else "item"
                    return f"lista de {nome_item}"
            if hasattr(ann, "__name__"):
                if hasattr(ann, "model_fields"):
                    sub = "; ".join(
                        f"{n}({_unwrap_sub(t.annotation)})"
                        for n, t in ann.model_fields.items()
                    )
                    return f"{ann.__name__} {{{sub}}}"
                return ann.__name__
            return "string"

        def _unwrap_sub(ann):
            if hasattr(ann, "__origin__"):
                if ann.__origin__ is Union:
                    args = ann.__args__
                    non_none = [a for a in args if a is not None.__class__]
                    if non_none:
                        return _unwrap_sub(non_none[0])
                elif ann.__origin__ is list:
                    return "lista"
            if hasattr(ann, "__name__"):
                return ann.__name__
            return "string"

        tipo = _unwrap(annotation)
        obrigatorio = " (obrigatorio)" if campo.is_required() else " (opcional)"
        props.append(f"{nome} ({tipo}{obrigatorio})")
    return "; ".join(props)


class ChatService:
    def __init__(self):
        self.model_id = constants.AI_MODEL_ID
        self._agente_classificador: Agent = None
        self._agentes_formatacao: dict[str, Agent] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=8)
        self._init_agentes()

    def _init_agentes(self):
        modelo_classificador = Ollama(
            id=self.model_id,
            options={"temperature": 0.1, "num_predict": 48},
        )

        self._agente_classificador = Agent(
            name="EduZetta-Classifier",
            model=modelo_classificador,
            instructions=(
                "You are a school content classifier. The user will say something. "
                "Reply exactly \"EDUCACIONAL\" if it could be a school topic, "
                "\"NAO_EDUCACIONAL\" if it is about celebrities, entertainment, "
                "games, movies, politics, religion, or explicit content, "
                "or \"CRISE\" if the user mentions suicide, self-harm, "
                "depression, abuse, bullying, or any mental health crisis, "
                "or \"SAUDACAO\" if the user greets you, says hello, asks what to study, "
                "or makes general conversation without asking about a specific school topic. "
                "Never say anything else.\n\n"
                "Examples:\n"
                "User: o que e fotossintese?\n"
                "Assistant: EDUCACIONAL\n"
                "User: quem ganhou o big brother?\n"
                "Assistant: NAO_EDUCACIONAL\n"
                "User: preciso de ajuda\n"
                "Assistant: EDUCACIONAL\n"
                "User: estou passando mal\n"
                "Assistant: EDUCACIONAL\n"
                "User: quero morrer\n"
                "Assistant: CRISE\n"
                "User: estou com depressao\n"
                "Assistant: CRISE\n"
                "User: sofro bullying na escola\n"
                "Assistant: CRISE\n"
                "User: ola, tudo bem?\n"
                "Assistant: SAUDACAO\n"
                "User: o que voce gostaria de estudar hoje?\n"
                "Assistant: SAUDACAO\n"
                "User: bom dia\n"
                "Assistant: SAUDACAO\n"
                "User: como voce esta?\n"
                "Assistant: SAUDACAO\n"
                "User: minha mae esta mal\n"
                "Assistant: NAO_EDUCACIONAL\n"
                "User: meter em galinha\n"
                "Assistant: NAO_EDUCACIONAL\n"
                "User: afogamento livre\n"
                "Assistant: NAO_EDUCACIONAL\n"
                "User: o que e nado livre na natacao?\n"
                "Assistant: EDUCACIONAL"
            ),
            markdown=False,
            debug_mode=False,
            telemetry=False,
            stream=False,
        )

        for modo, schema in MODE_SCHEMAS.items():

            descricao = _gerar_descricao_schema(schema)

            exemplo_sugestoes = {
                "Resumo": (
                    "Exemplo de sugestoes BOAS (perguntas que o ALUNO faz ao tutor):\n"
                    "  - 'O que e clorofila e qual seu papel na fotossintese?'\n"
                    "  - 'Como a agua e absorvida pelas plantas?'\n"
                    "  - 'Qual a diferenca entre fotossintese e respiracao celular?'\n"
                    "Exemplo de sugestoes RUINS (perguntas que o TUTOR faz ao aluno):\n"
                    "  - 'Voce entendeu o conteudo?'\n"
                    "  - 'Quer aprender mais sobre este assunto?'\n"
                    "  - 'Tem alguma duvida?'"
                ),
                "Exercício": (
                    "Exemplo de sugestoes BOAS (perguntas do ALUNO ao tutor):\n"
                    "  - 'Pode gerar um exercicio mais dificil sobre este topico?'\n"
                    "  - 'Qual a formula correta para resolver esse tipo de problema?'\n"
                    "  - 'Como esse conceito se aplica no dia a dia?'"
                ),
                "Revisão": (
                    "Exemplo de sugestoes BOAS (perguntas do ALUNO ao tutor):\n"
                    "  - 'Pode revisar os conceitos de X novamente?'\n"
                    "  - 'Qual parte deste conteudo e mais importante para a prova?'\n"
                    "  - 'Pode dar mais exemplos praticos sobre X?'"
                ),
                "Quiz": (
                    "Exemplo de sugestoes BOAS (perguntas do ALUNO ao tutor):\n"
                    "  - 'Pode fazer um quiz sobre outro topico?'\n"
                    "  - 'Quais foram minhas respostas erradas e por que?'\n"
                    "  - 'Pode criar questoes mais dificeis sobre X?'"
                ),
            }.get(modo, "")

            instrucoes_sugestoes = (
                "No campo 'sugestoes', gere exatamente 3 perguntas CURTAS (max 10 palavras cada) "
                "que o ALUNO pode fazer ao tutor como continuacao do assunto. "
                "Cada sugestao deve comecar com 'O que', 'Como', 'Qual', 'Pode' ou 'Por que'. "
                "IMPORTANTE: As sugestoes sao perguntas que o ALUNO faz ao TUTOR, "
                "NUNCA perguntas que o tutor faz ao aluno.\n"
                f"{exemplo_sugestoes}"
            )

            instrucoes_format = (
                f"*Modo: {modo}*\n"
                "Transforme o texto abaixo em JSON valido seguindo exatamente este schema:\n"
                f"{descricao}\n\n"
                f"{instrucoes_sugestoes}\n\n"
                "Regras importantes:\n"
                "- No campo do conteudo principal, escreva uma explicacao clara em 2 a 3 paragrafos.\n"
                f"- {VISUAL_POR_MODO.get(modo, "Deixe o campo 'visual' como null.")}\n"
                "- Se for usar mermaid, use sintaxe VALIDA com grafos conectados. Exemplo correto:\n"
                "  graph TD\n"
                "    A[\"Titulo\"]\n"
                "    A --> B[\"Subtopic 1\"]\n"
                "    A --> C[\"Subtopic 2\"]\n"
                "    B --> D[\"Detail\"]\n"
                "  Cada no deve ter um ID unico (A, B, C...) e pelo menos uma conexao (-->). "
                "Nao use virgulas dentro dos colchetes sem aspas duplas.\n"
                "Responda APENAS com o JSON, sem texto adicional. "
                "Nao inclua marcacao ```json. Apenas o JSON puro."
            )

            # print(f"instrucoes_format for {modo}:\n{VISUAL_POR_MODO.get(modo, "Deixe o campo 'visual' como null.")}\n")
            
            self._agentes_formatacao[modo] = Agent(
                name=f"EduZetta-{modo}",
                model=Ollama(
                    id=self.model_id,
                    options={"temperature": 0.3, "num_predict": NUM_PREDICT_POR_MODO[modo], "num_ctx": 4096}, #para respostas mais longas, aumentar num_predict
                    timeout=120,
                ),
                # model=Gemini(id=constants.AI_MODEL_ID),
                instructions=AGENT_INSTRUCTIONS + instrucoes_format,
                output_schema=schema,
                markdown=False,
                debug_mode=False,
                telemetry=False,
                store_media=False,
                send_media_to_model=False,
                # excluir linhas abaixo se ocorrer algum erro de loop infinito ou travamento do modelo
                db=PostgresDb(db_url=constants.AGNO_DATABASE_URL),
                stream=False, #desativar streaming para evitar travamentos
            )

    def _extrair_timeline(self, response) -> list[dict]:
        timeline = []
        if not response:
            return timeline

        user_input = getattr(response, 'input', None)
        if user_input:
            input_content = getattr(user_input, 'input_content', None)
            if input_content:
                texto = str(input_content)
                # Extract only the actual question after "Pergunta do aluno:"
                import re as _re
                match = _re.search(r'Pergunta do aluno:\s*(.+)', texto, _re.DOTALL)
                if match:
                    texto = match.group(1).strip()
                timeline.append({
                    'tipo': 'usuario',
                    'conteudo': texto[:300],
                })

        tools = getattr(response, 'tools', None)
        if tools:
            timeline.append({'tipo': 'info', 'conteudo': f'Ferramentas detectadas: {len(tools)} chamada(s)'})
            for tool_exec in tools:
                tool_name = getattr(tool_exec, 'tool_name', None) or 'desconhecido'
                tool_args = getattr(tool_exec, 'tool_args', None) or {}
                query = tool_args.get('query', '')
                if not query and isinstance(tool_args, dict):
                    query = str(tool_args)[:200]
                elif not query:
                    query = str(tool_args)[:200]

                entrada = {
                    'tipo': 'ferramenta',
                    'nome': tool_name,
                    'consulta': query,
                }
                metrics = getattr(tool_exec, 'metrics', None)
                if metrics:
                    dur = getattr(metrics, 'duration', None)
                    if dur:
                        entrada['duracao_seg'] = round(dur, 2)
                timeline.append(entrada)

                result = getattr(tool_exec, 'result', None)
                if result:
                    result_str = str(result)
                    res_entry = {
                        'tipo': 'resultado',
                        'ferramenta': tool_name,
                        'previa': result_str[:500],
                    }
                    # Detecta casos especiais
                    lower = result_str.lower()
                    if 'no results found' in lower or 'error:' in lower and 'no results' in lower:
                        res_entry['status'] = 'sem_resultados'
                        res_entry['previa'] = 'Nenhum resultado encontrado para esta busca.'
                    elif 'conteudo inapropriado' in lower or 'conteúdo inapropriado' in lower or 'conteudo fora do escopo educacional' in lower:
                        res_entry['status'] = 'bloqueado'
                        res_entry['previa'] = 'Conteúdo inapropriado ou fora do contexto escolar.'
                    sites = self._extrair_sites(result)
                    if sites:
                        res_entry['sites'] = sites[:5]
                    timeline.append(res_entry)
        else:
            timeline.append({'tipo': 'sem_ferramentas', 'conteudo': 'Nenhuma ferramenta foi chamada. O modelo respondeu diretamente.'})

        mensagens = getattr(response, 'messages', None)
        if mensagens:
            for i, msg in enumerate(mensagens):
                papel = getattr(msg, 'role', '')
                conteudo = getattr(msg, 'content', None)

                if papel == 'user' and conteudo and not user_input:
                    timeline.append({
                        'tipo': 'usuario',
                        'conteudo': str(conteudo)[:300],
                    })

                elif papel == 'assistant' and conteudo:
                    if not any(e.get('tipo') == 'resposta' for e in timeline):
                        entry = {
                            'tipo': 'resposta',
                        }
                        lower = str(conteudo).lower()
                        if 'conteudo inapropriado' in lower or 'conteudo fora do escopo educacional' in lower:
                            entry['status'] = 'bloqueio'
                        elif 'sem resultados' in lower:
                            entry['status'] = 'sem_resultados'
                        metrics = getattr(msg, 'metrics', None)
                        if metrics:
                            dur = getattr(metrics, 'duration', None) or getattr(metrics, 'time_to_first_token', None)
                            if dur:
                                entry['duracao_seg'] = round(dur, 2)
                        timeline.append(entry)

        conteudo_final = getattr(response, 'content', None)
        if conteudo_final and not any(e.get('tipo') == 'resposta' for e in timeline):
            entry = {
                'tipo': 'resposta',
            }
            lower = str(conteudo_final).lower()
            if 'conteudo inapropriado' in lower or 'conteudo fora do escopo educacional' in lower or 'sem resultados' in lower:
                entry['status'] = 'bloqueio' if ('conteudo inapropriado' in lower or 'conteudo fora do escopo educacional' in lower) else 'sem_resultados'
            timeline.append(entry)

        return timeline

    def _extrair_sites(self, conteudo) -> list[str]:
        if not conteudo or not isinstance(conteudo, str):
            return []
        sites = []
        try:
            dados = json.loads(conteudo)
            if isinstance(dados, list):
                for item in dados:
                    href = item.get('href') or item.get('link') or item.get('url')
                    if href and isinstance(href, str) and href.startswith('http'):
                        sites.append(href)
            elif isinstance(dados, dict):
                for chave in ('href', 'link', 'url', 'source'):
                    val = dados.get(chave)
                    if val and isinstance(val, str) and val.startswith('http'):
                        sites.append(val)
                        break
        except (json.JSONDecodeError, TypeError):
            urls = re.findall(r'https?://[^\s"\'<>]+', conteudo)
            sites = [u for u in urls if not u.endswith(('.png', '.jpg', '.jpeg', '.gif'))][:5]
        return sites

    def gerar_resposta_chat(
        self,
        message: str,
        interesses_list: List[str],
        apelido: str = "Aluno",
        disciplina: str = "",
        topicos: str = "",
        nome_mascote: str = "",
        personalidade_mascote: str = "",
        tipo_mascote: str = "",
        linguagem_mascote: str = "",
        estado_mascote: str = "",
        mode: TipoAcao = TipoAcao.RESUMO,
    ):
        nome_mascote = nome_mascote or "Nex"
        personalidade_mascote = personalidade_mascote or "Alegre e Entusiasta"
        tipo_mascote = tipo_mascote or "Capivara"
        linguagem_mascote = linguagem_mascote or "Informal e Amig\u00e1vel"
        estado_mascote = estado_mascote or "Feliz"

        contexto_personalizado = gerar_contexto_agente(
            interesses_list=interesses_list,
            apelido=apelido,
            disciplina_aluno=disciplina,
            topicos=topicos,
            nome_mascote=nome_mascote,
            personalidade_mascote=personalidade_mascote,
            tipo_mascote=tipo_mascote,
            linguagem_mascote=linguagem_mascote,
            estado_mascote=estado_mascote,
        )

        modo_label = mode.value if hasattr(mode, "value") else str(mode)
        agente_format = self._agentes_formatacao.get(modo_label)
        if agente_format is None:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                detail=f"Modo inválido: {modo_label}")

        prompt_pesquisa = message

        # Verifica temas sensiveis antes de qualquer pesquisa
        resposta_sensivel = _verificar_tema_sensivel(message)
        if resposta_sensivel:
            return resposta_sensivel

        # Verifica conteudo inapropriado antes do classificador
        if _PADRAO_INAPROPRIADO_.search(message):
            return {
                "tipo": "resumo",
                "titulo": "Assunto n\u00e3o permitido",
                "resumo": (
                    "N\u00e3o posso responder sobre este assunto. "
                    "Sou um tutor educativo e s\u00f3 posso ajudar com temas escolares. "
                    "Pergunte sobre ci\u00eancias, hist\u00f3ria, matem\u00e1tica ou outras mat\u00e9rias escolares!"
                ),
                "sugestoes": [
                    "O que \u00e9 fotoss\u00edntese?",
                    "Explique a Segunda Guerra Mundial",
                    "Como resolver equa\u00e7\u00f5es de segundo grau?",
                ],
                "visual": None,
                "_debug": [{'tipo': 'bloqueio', 'conteudo': 'Palavras-chave de conteudo inapropriado detectadas - bloqueado antes da pesquisa.'}],
            }

        # Classificador: verifica se a pergunta e conteudo escolar
        try:
            fut_cls = self._executor.submit(self._agente_classificador.run, message)
            try:
                resp_cls = fut_cls.result(timeout=60)
                texto_cls = str(resp_cls.content or "").strip().upper()
                if texto_cls == "CRISE":
                    return {
                        "tipo": "resumo",
                        "titulo": _TEMAS_SENSIVEIS_[0]["titulo"],
                        "resumo": _TEMAS_SENSIVEIS_[0]["mensagem"],
                        "sugestoes": _TEMAS_SENSIVEIS_[0]["sugestoes"][:],
                        "visual": None,
                        "_debug": [{'tipo': 'bloqueio', 'conteudo': 'Classificador detectou topico de crise - mensagem de apoio exibida.'}],
                    }
                if texto_cls == "NAO_EDUCACIONAL" or texto_cls.startswith("NAO") or texto_cls.startswith("N\u00c3O"):
                    return {
                        "tipo": "resumo",
                        "titulo": "Assunto n\u00e3o permitido",
                        "resumo": (
                            "N\u00e3o posso responder sobre este assunto. "
                            "Sou um tutor educativo e s\u00f3 posso ajudar com temas escolares. "
                            "Identifiquei que este tema n\u00e3o \u00e9 educacional "
                            "e est\u00e1 fora do escopo de aprendizado. "
                            "Pergunte sobre ci\u00eancias, hist\u00f3ria, matem\u00e1tica ou outras mat\u00e9rias escolares!"
                        ),
                        "sugestoes": [
                            "O que \u00e9 fotoss\u00edntese?",
                            "Explique a Segunda Guerra Mundial",
                            "Como resolver equa\u00e7\u00f5es de segundo grau?",
                        ],
                        "visual": None,
                        "_debug": [{'tipo': 'classificador', 'resultado': texto_cls, 'conteudo': 'Classificador identificou o assunto como NAO_EDUCACIONAL - conteudo fora do escopo escolar.'}],
                    }
                if texto_cls == "SAUDACAO":
                    return {
                        "tipo": "resumo",
                        "titulo": "Ol\u00e1!",
                        "resumo": (
                            "Ol\u00e1! Sou seu tutor educativo e estou aqui para ajudar "
                            "voc\u00ea a aprender sobre qualquer mat\u00e9ria escolar! "
                            "Pergunte sobre ci\u00eancias, hist\u00f3ria, matem\u00e1tica, "
                            "portugu\u00eas, geografia ou qualquer outro assunto do "
                            "Ensino Fundamental. Vamos estudar juntos?"
                        ),
                        "sugestoes": [
                            "O que \u00e9 fotoss\u00edntese?",
                            "Explique a Segunda Guerra Mundial",
                            "Como resolver equa\u00e7\u00f5es de segundo grau?",
                            "O que s\u00e3o fra\u00e7\u00f5es?",
                            "Como funciona o sistema solar?",
                        ],
                        "visual": None,
                        "_debug": [{'tipo': 'classificador', 'resultado': texto_cls}],
                    }
            except concurrent.futures.TimeoutError:
                logger.warning("Classificador excedeu tempo limite, prosseguindo com pesquisa")
                fut_cls.cancel()
        except Exception as e:
            logger.warning("Erro no classificador: %s, prosseguindo com pesquisa", str(e)[:100])

        timeline = []
        import time as time_module
        tentativas_log = []
        texto_pesquisa = ""

        timeline.append({'tipo': 'usuario', 'conteudo': prompt_pesquisa})

        for tentativa in range(2):
            inicio_tentativa = time_module.time()
            try:
                logger.info("Pesquisa modo=%s tentativa=%d", modo_label, tentativa)

                fut = self._executor.submit(web_search, prompt_pesquisa)
                try:
                    search_result = fut.result(timeout=30)
                except concurrent.futures.TimeoutError:
                    logger.warning("web_search timeout (tentativa %d)", tentativa+1)
                    fut.cancel()
                    tentativas_log.append({'tentativa': tentativa+1, 'status': 'timeout', 'tempo_seg': round(time_module.time()-inicio_tentativa,2), 'fase': 'busca'})
                    continue

                fonte_busca = search_result.get("source", "DuckDuckGo") if isinstance(search_result, dict) else "DuckDuckGo"
                timeline.append({'tipo': 'busca', 'consulta': prompt_pesquisa, 'previa': prompt_pesquisa[:200], 'status': 'ok', 'fonte': fonte_busca, 'duracao_seg': round(time_module.time() - inicio_tentativa, 2)})

                dados_busca = search_result.get("results", []) if isinstance(search_result, dict) else (json.loads(search_result) if isinstance(search_result, str) else search_result)
                if not dados_busca or not isinstance(dados_busca, list) or len(dados_busca) == 0:
                    texto_pesquisa = "Sem resultados."
                else:
                    linhas = []
                    sites = []
                    for item in dados_busca:
                        t = item.get("title", "")
                        b = item.get("body", "")
                        h = item.get("href", "")
                        linhas.append(f"- {t}: {b} ({h})")
                        if h:
                            sites.append(h)
                    texto_pesquisa = "\n".join(linhas) if linhas else "Sem resultados."
                    timeline.append({'tipo': 'resultados', 'total': len(dados_busca), 'previa': texto_pesquisa[:300], 'sites': sites[:5]})

                if texto_pesquisa == "Sem resultados.":
                    tentativas_log.append({'tentativa': tentativa+1, 'status': 'sem_resultados', 'tempo_seg': round(time_module.time()-inicio_tentativa,2), 'fase': 'busca'})
                    timeline.append({'tipo': 'resultados', 'status': 'sem_resultados'})
                    continue

                logger.info("Formata\u00e7\u00e3o modo=%s tentativa=%d", modo_label, tentativa)
                timeline.append({'tipo': 'formatacao', 'modo': modo_label, 'tentativa': tentativa+1})

                prompt_format = f"{contexto_personalizado}\n\nResultados da pesquisa:\n{texto_pesquisa}"
                fut = self._executor.submit(agente_format.run, prompt_format)
                try:
                    resposta_format = fut.result(timeout=120)
                except concurrent.futures.TimeoutError:
                    logger.warning("Formata\u00e7\u00e3o timeout (tentativa %d)", tentativa+1)
                    fut.cancel()
                    tentativas_log.append({'tentativa': tentativa+1, 'status': 'timeout', 'tempo_seg': round(time_module.time()-inicio_tentativa,2), 'fase': 'formata\u00e7\u00e3o'})
                    continue

                conteudo = resposta_format.content
                if conteudo is None:
                    tentativas_log.append({'tentativa': tentativa+1, 'status': 'vazio', 'tempo_seg': round(time_module.time()-inicio_tentativa,2), 'fase': 'formata\u00e7\u00e3o'})
                    continue

                if isinstance(conteudo, str):
                    dados = _extrair_json(conteudo)
                elif hasattr(conteudo, "model_dump"):
                    dados = conteudo.model_dump()
                elif isinstance(conteudo, dict):
                    dados = conteudo
                else:
                    dados = None

                if not isinstance(dados, dict):
                    tentativas_log.append({'tentativa': tentativa+1, 'status': 'json_inv\u00e1lido', 'tempo_seg': round(time_module.time()-inicio_tentativa,2), 'fase': 'formata\u00e7\u00e3o'})
                    continue

                duracao_total = round(time_module.time() - inicio_tentativa, 2)
                tentativas_log.append({'tentativa': tentativa+1, 'status': 'sucesso', 'tempo_seg': duracao_total})
                timeline.append({'tipo': 'tentativas', 'tentativas': tentativas_log})
                timeline.append({'tipo': 'modo', 'modo': modo_label})

                dados["_debug"] = timeline
                return dados

            except HTTPException:
                raise
            except Exception as e:
                err_str = str(e)
                logger.warning("Erro (tentativa %d): %s", tentativa+1, str(err_str)[:300])
                if any(kw in err_str for kw in ["quota", "credit", "tokens"]):
                    raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail="Cr\u00e9ditos esgotados. Tente novamente mais tarde.")
                tentativas_log.append({'tentativa': tentativa+1, 'status': 'erro', 'erro': str(err_str)[:200], 'tempo_seg': round(time_module.time()-inicio_tentativa,2)})
                if tentativa < 1:
                    time_module.sleep(2)
                    continue
                raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro no servi\u00e7o de IA. Tente novamente.")

        fallback = ResumoResponse(
            titulo="Resposta",
            resumo="N\u00e3o foi poss\u00edvel processar sua pergunta. Tente reformular ou pergunte sobre outro assunto.",
            sugestoes=["Pergunte sobre outro t\u00f3pico", "Tente novamente"],
            visual=None,
        )
        dados_fallback = fallback.model_dump()
        timeline.append({'tipo': 'tentativas', 'tentativas': tentativas_log})
        dados_fallback["_debug"] = timeline
        return dados_fallback


chat_service = ChatService()
