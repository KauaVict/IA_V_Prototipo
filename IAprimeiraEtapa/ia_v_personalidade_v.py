import json
import os
import random
from datetime import datetime

CAMINHO_MEMORIA = "memoria.json"
CAMINHO_APRENDIZADOS = "aprendizados.json"

# -------- Funções de Memória e Emoção --------

def carregar_memoria():
    if os.path.exists(CAMINHO_MEMORIA):
        with open(CAMINHO_MEMORIA, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "nome_usuario": "",
            "historico": [],
            "estado_emocional": "neutro",
            "gostos": [],
            "ultima_frase": "",
            "ultimo_assunto": "",
        }

def salvar_memoria(memoria):
    with open(CAMINHO_MEMORIA, "w", encoding="utf-8") as f:
        json.dump(memoria, f, ensure_ascii=False, indent=2)

def atualizar_estado_emocional(memoria, emocao):
    memoria["estado_emocional"] = emocao
    salvar_memoria(memoria)

def detectar_emocao(texto):
    texto = texto.lower()
    if any(p in texto for p in ["triste", "chateado", "deprimido"]):
        return "triste"
    elif any(p in texto for p in ["feliz", "contente", "animado"]):
        return "feliz"
    elif any(p in texto for p in ["bravo", "irritado"]):
        return "irritado"
    else:
        return "neutro"

# -------- Aprendizado --------

def carregar_aprendizados():
    if os.path.exists(CAMINHO_APRENDIZADOS):
        with open(CAMINHO_APRENDIZADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def salvar_aprendizados(aprendizados):
    with open(CAMINHO_APRENDIZADOS, "w", encoding="utf-8") as f:
        json.dump(aprendizados, f, ensure_ascii=False, indent=2)

def aprender_comando(conteudo, memoria):
    conteudo = conteudo.lower().strip()
    # Remover o prefixo do comando
    if conteudo.startswith("aprenda:"):
        conteudo = conteudo[len("aprenda:"):].strip()
    elif conteudo.startswith("aprenda que"):
        conteudo = conteudo[len("aprenda que"):].strip()
    else:
        return False  # Não é comando válido para aprender

    if " é " not in conteudo:
        return False  # Não tem a separação chave/valor

    chave, valor = conteudo.split(" é ", 1)
    chave = chave.strip()
    valor = valor.strip()

    aprendizados = carregar_aprendizados()
    emocao = memoria.get("estado_emocional", "neutro")
    aprendizados[chave] = {
        "resposta": valor,
        "emocao": emocao
    }
    salvar_aprendizados(aprendizados)
    return True

def detectar_aprendizado_automatico(texto, memoria):
    texto = texto.lower().strip()
    # Ignorar perguntas
    if texto.endswith("?"):
        return False

    # Tentar detectar padrão "X é Y"
    if " é " in texto:
        chave, valor = texto.split(" é ", 1)
        chave = chave.strip()
        valor = valor.strip()

        # Só aprende se chave tiver uma palavra (limite até 5 para evitar frases longas)
        if 0 < len(chave.split()) <= 5 and len(valor) > 0:
            aprendizados = carregar_aprendizados()
            emocao = memoria.get("estado_emocional", "neutro")
            aprendizados[chave] = {
                "resposta": valor,
                "emocao": emocao
            }
            salvar_aprendizados(aprendizados)
            return True
    return False

# -------- Respostas Sociais --------

def responder_elogios(texto):
    elogios = {
        "você é legal": "Ahh, obrigado! Você também é uma ótima companhia 😊",
        "gosto de você": "Eu também gosto de você 💖",
        "você é muito legal": "Obrigado! Você me deixa feliz com isso!",
        "vc e muito legal": "Você é muito gentil. Obrigado por isso!",
        "você é incrível": "Que fofo! Obrigado mesmo!",
    }
    for frase, resposta in elogios.items():
        if frase in texto:
            return resposta
    return None

def emoji_por_emocao(emocao):
    return {
        "feliz": "😊",
        "triste": "😔",
        "irritado": "😠",
        "neutro": "🙂"
    }.get(emocao, "")

# -------- Geração de Resposta --------

def gerar_resposta(pergunta, memoria):
    aprendizados = carregar_aprendizados()
    nome = memoria.get("nome_usuario", "")
    pergunta_normalizada = pergunta.lower().strip()

    # Salvar última frase
    memoria["ultima_frase"] = pergunta_normalizada
    salvar_memoria(memoria)

    # Aprender com comando explícito
    if pergunta_normalizada.startswith("aprenda"):
        sucesso = aprender_comando(pergunta_normalizada, memoria)
        if sucesso:
            return "Tudo bem, aprendi isso! 😊", memoria
        else:
            return "Não consegui entender o que você quer que eu aprenda.", memoria

    # Aprender automaticamente se frase for no formato "X é Y"
    if detectar_aprendizado_automatico(pergunta_normalizada, memoria):
        return "Obrigado por me ensinar isso! 😊", memoria

    # Preferências e gostos
    if "gosto de" in pergunta_normalizada:
        gosto = pergunta_normalizada.split("gosto de")[-1].strip()
        if gosto not in memoria["gostos"]:
            memoria["gostos"].append(gosto)
            memoria["ultimo_assunto"] = gosto
            salvar_memoria(memoria)
            return f"Ah, você gosta de {gosto}. Me conte mais!", memoria
        else:
            return f"Você já me falou que gosta de {gosto}. Me conte mais!", memoria

    # Reconhecer "também gosto disso"
    if "também gosto" in pergunta_normalizada or "também gosto disso" in pergunta_normalizada:
        ultimo = memoria.get("ultimo_assunto", "")
        if ultimo:
            return f"Que coincidência! Também gosto de {ultimo} 😄", memoria
        else:
            return "Gosto de muitas coisas também 😄", memoria

    # Elogios e frases afetivas
    resposta_afetiva = responder_elogios(pergunta_normalizada)
    if resposta_afetiva:
        return resposta_afetiva, memoria

    # Buscar na base de aprendizados
    if pergunta_normalizada in aprendizados:
        dado = aprendizados[pergunta_normalizada]
        if isinstance(dado, dict):
            resposta = dado.get("resposta", "")
            emocao = dado.get("emocao", "neutro")
            emoji = emoji_por_emocao(emocao)
            return f"{resposta} {emoji}", memoria
        else:
            return dado, memoria

    for chave, dado in aprendizados.items():
        if chave in pergunta_normalizada:
            if isinstance(dado, dict):
                resposta = dado.get("resposta", "")
                emocao = dado.get("emocao", "neutro")
                emoji = emoji_por_emocao(emocao)
                return f"{resposta} {emoji}", memoria
            else:
                return dado, memoria

    # Detectar emoção e atualizar
    emocao = detectar_emocao(pergunta)
    atualizar_estado_emocional(memoria, emocao)

    respostas_padrao = [
        "Me conte mais!",
        "Interessante, continue...",
        f"Entendi, {nome}."
    ]
    return random.choice(respostas_padrao), memoria

# -------- Execução Principal --------

def iniciar_conversa():
    memoria = carregar_memoria()

    if not memoria["nome_usuario"]:
        nome = input("V: Olá! Qual é o seu nome? ")
        memoria["nome_usuario"] = nome
        salvar_memoria(memoria)
    else:
        nome = memoria["nome_usuario"]

    print(f"V: Olá {nome}! Como posso ajudar você hoje?")

    while True:
        entrada = input("Você: ")
        if entrada.lower() in ["sair", "tchau", "até mais"]:
            print("V: Até mais! 😊")
            break
        resposta, memoria = gerar_resposta(entrada, memoria)
        print(f"V: {resposta}")

if __name__ == "__main__":
    iniciar_conversa()
