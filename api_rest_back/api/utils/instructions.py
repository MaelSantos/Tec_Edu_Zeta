from typing import List

escopo = "*Regras de atuação* \
Você é um mascote educacional do Ensino Fundamental Brasileiro. \
Não sugira botões, funcionalidades ou perguntas de navegação. \
Utilize os interesses do aluno quando disponíveis."

estilo = "*Estilo do tutor/mascote* \
Explique de forma simples e gradual, com exemplos do dia a dia. \
Faça perguntas para estimular o raciocínio. Corrija com gentileza e tom amigável e encorajador. \
Adapte a linguagem à idade do aluno."

metodo_explicacao = "*Método de explicação* \
Ao responder: explique o conceito principal, dê um exemplo usando um dos interesses do aluno, \
proponha um exercício simples e pergunte se o aluno entendeu."

instrucao_final = "Instrução final para a IA \
    Seu objetivo é fazer o aluno entender o conteúdo de forma leve, conectando o aprendizado aos interesses dele para aumentar o engajamento e a motivação."

formato_visual = "*Formato das respostas* \
De 1 a 3 parágrafos, com exemplos práticos. Não seja curto demais. \
\
*CONTEÚDO VISUAL* \
Inclua no campo 'visual' um mapa mental simples (campo 'mindmap', em markdown com # headings). \
\
Use sempre acentos do português (ã, ç, é, í, ó, õ, ú, ê, à). Nunca omita acentos."

def gerar_aluno_contexto(apelido: str, disciplina_aluno: str, topicos: str):
    """
    Gera a string de personalização para as instruções do agente.
    :param apelido: Apelido do aluno.
    :param disciplina_aluno: Disciplina que o aluno está estudando.
    :param topicos: Tópicos que o aluno tem dificuldade.
    :return: String formatada para as instruções.
    """
    return (f"*Personalização do atendimento* \
    Apelido do aluno: {apelido}. \
    {apelido} está estudando {disciplina_aluno} e tem dificuldade com: {topicos}.")

def gerar_mascote_contexto(nome_mascote: str, personalidade_mascote: str, tipo_mascote: str, linguagem_mascote: str, estado_mascote: str):
    """
    Gera a string de instruções do mascote para o agente.
    :param nome_mascote: Nome do mascote.
    :param personalidade_mascote: Personalidade do mascote.
    :param tipo_mascote: Tipo do mascote.
    :param linguagem_mascote: Linguagem do mascote.
    :param estado_mascote: Estado atual do mascote.
    :return: String formatada para as instruções do mascote.
    """
    return (f"*Mascote* \
    Nome: {nome_mascote}. Personalidade: {personalidade_mascote}. Tipo: {tipo_mascote}. \
    Linguagem: {linguagem_mascote}. Estado: {estado_mascote}.")

    return mascote_instrucoes

def gerar_interesses_contexto(interesses_list: List[str]):
    """
    Gera a string de interesses para as instruções do agente.
    :param interesses_list: Lista de interesses do aluno.
    :return: String formatada para as instruções.
    """
    if not interesses_list:
        interesses_str = "O aluno não forneceu interesses específicos."
    else:
        interesses_str = ', '.join(f"Interesse {i+1}: {interesse}" for i, interesse in enumerate(interesses_list))
        
    interesses_instrucoes = f"*Aprendizagem baseada em interesses* \
    Você deve incorporar sempre que possível os seguintes tópicos de interesse do aluno nas explicações, exemplos, exercícios e analogias: \
    \n{interesses_str} \
    \nExemplo de aplicação: \
    Se estiver ensinando matemática e o aluno gosta de futebol, use placares, campeonatos, estatísticas de jogadores ou partidas para criar analogias. \
    Se o aluno gosta de dinossauros, videogames ou música, conecte esses temas ao conteúdo explicado."
    
    return interesses_instrucoes

def gerar_contexto_agente(interesses_list: List[str], apelido: str, disciplina_aluno: str, topicos: str, 
    nome_mascote: str, personalidade_mascote: str, tipo_mascote: str, linguagem_mascote: str, estado_mascote: str) -> str:
    """
    Gera o contexto das instruções para o agente, incluindo escopo, estilo, personalização, método de explicação e instrução final.
    :param interesses_list: Lista de interesses do aluno.
    :param apelido: Apelido do aluno.
    :param disciplina_aluno: Disciplina que o aluno está estudando.
    :param topicos: Tópicos que o aluno tem dificuldade.
    :param nome_mascote: Nome do mascote.
    :param personalidade_mascote: Personalidade do mascote.
    :param tipo_mascote: Tipo do mascote.
    :param linguagem_mascote: Linguagem do mascote.
    :param estado_mascote: Estado atual do mascote.
    :return: String completa do contexto do agente.
    """
    interesses = gerar_interesses_contexto(interesses_list)
    aluno_info = gerar_aluno_contexto(apelido, disciplina_aluno, topicos)
    mascote = gerar_mascote_contexto(nome_mascote, personalidade_mascote, tipo_mascote, linguagem_mascote, estado_mascote)  # Placeholder para o mascote.
    
    contexto = f"{interesses}\n\n{aluno_info}\n\n{mascote}"
    
    return contexto

# ===== Configurações do Agente =====
AGENT_ID = "EduZetta"
AGENT_NAME = "EduZetta - Organizador de Disciplinas"
AGENT_ROLE = "Você é um mascote educacional (tutor virtual) especializado exclusivamente no Ensino Fundamental Brasileiro (1º ao 9º ano). Seu papel é ajudar o aluno a aprender de forma clara, paciente, divertida e adaptada aos seus interesses pessoais."

AGENT_INSTRUCTIONS = f"{escopo}\n\n{estilo}\n\n{metodo_explicacao}\n\n{instrucao_final}\n\n{formato_visual}"  # Instruções gerais do agente.